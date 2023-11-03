import os

import pymysql
from config import (
    BASE_SCHEMA,
    assert_tables,
    make_postgres_connection,
    print_tables_in_schema,
    set_up_schemas,
    truncate_tables,
)
from models import (
    Appointment,
    CashPayment,
    Doctor,
    LineItem,
    LineItemTransaction,
    Office,
    Patient,
    tables,
)

table_classes = [
    Doctor,
    Patient,
    Office,
    Appointment,
    LineItem,
    CashPayment,
    LineItemTransaction,
]


def create_tables(connection):
    with connection.cursor() as cursor:
        # get the .create_table() method from each class, and then call it with `cursor` as its arg.
        for table_class in table_classes:
            getattr(table_class, "create_table")(cursor)
    connection.commit()


def count_rows_in_tables(cursor):
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {BASE_SCHEMA}.{table};")
        count = cursor.fetchone()[0]
        print(f"The number of rows in the {table} table is {count}")


def populate_tables(connection, num_doctors=500, num_patients=12, num_appointments=20):
    def fetch_all_ids(cursor, table_name):
        cursor.execute(f"SELECT id FROM {BASE_SCHEMA}.{table_name}")
        return [row[0] for row in cursor.fetchall()]

    def fetch_ids_and_doctor_ids(cursor, table_name):
        query = f"SELECT id, doctor_id FROM {BASE_SCHEMA}.{table_name}"
        cursor.execute(query)
        return [(row[0], row[1]) for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        doctors = Doctor.populate(cursor, n=num_doctors)
        offices = Office.populate(cursor, doctors, n=5)
        patients = Patient.populate(cursor, doctors, n=num_patients)

        # Fetch IDs of inserted Doctors, Offices, and Patients
        doctor_ids = fetch_all_ids(cursor, "doctor")
        office_data = fetch_ids_and_doctor_ids(cursor, "office")
        patient_data = fetch_ids_and_doctor_ids(cursor, "patient")

        # Create Python objects for doctors, offices, and patients with the fetched IDs
        doctors = [Doctor(id=i) for i in doctor_ids]
        offices = [Office(id=i, doctor_id=d) for i, d in office_data]
        patients = [Patient(id=i, doctor_id=d) for i, d in patient_data]

        Appointment.populate(cursor, patients, offices, n=num_appointments)
        connection.commit()
        LineItem.populate(cursor, n=2)
        CashPayment.populate(cursor)
        # connection.commit()
        LineItemTransaction.populate(cursor)
        connection.commit()

    print("Done populating the tables!")


def make_mvs(connection):
    from matviews import (
        ds_credits_creation_sql,
        ds_debits_creation_sql,
        ds_pp_creation_sql,
    )
    from psycopg2.errors import DuplicateTable

    with connection.cursor() as cursor:
        for ds_sql in [
            ds_debits_creation_sql,
            ds_pp_creation_sql,
            ds_credits_creation_sql,
        ]:
            try:
                cursor.execute(ds_sql)
            except DuplicateTable as e:
                pass

    connection.commit()


if __name__ == "__main__":
    connection = make_postgres_connection()
    set_up_schemas(connection)
    truncate_tables(connection)
    create_tables(connection)
    print_tables_in_schema(connection)
    assert_tables(connection, table_classes)
    populate_tables(connection, num_doctors=10)  # start small just to test every table
    populate_tables(connection, num_doctors=490)
    make_mvs(connection)
