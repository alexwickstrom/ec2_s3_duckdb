import os

import pymysql

from config import make_postgres_connection
from factories import AppointmentFactory, DoctorFactory, LineItemFactory, PatientFactory
from models import (
    Doctor,
    Patient,
    Appointment,
    CashPayment,
    LineItem,
    LineItemTransaction,
    tables,
)


def truncate_tables(connection):
    with connection.cursor() as cursor:
        for table_name in tables:
            cursor.execute("DROP TABLE IF EXISTS {} CASCADE;".format(table_name))


def create_tables(connection):
    with connection.cursor() as cursor:
        DoctorFactory.create_table(cursor)
        PatientFactory.create_table(cursor)
        Appointment.create_table(cursor)
        LineItem.create_table(cursor)
        CashPayment.create_table(cursor)
        LineItemTransaction.create_table(cursor)
    connection.commit()


def count_rows_in_tables(cursor):
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"The number of rows in the {table} table is {count}")


def populate_tables(connection, num_doctors=150, num_patients=12, num_appointments=20):
    def fetch_all_ids(cursor, table_name):
        cursor.execute(f"SELECT id FROM {table_name}")
        return [row[0] for row in cursor.fetchall()]

    def fetch_ids_and_doctor_ids(cursor, table_name):
        query = f"SELECT id, doctor_id FROM {table_name}"
        cursor.execute(query)
        return [(row[0], row[1]) for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        doctors = DoctorFactory.populate(cursor, n=num_doctors)
        patients = Patient.populate(cursor, doctors, n=num_patients)
        # Fetch IDs of inserted Doctors and Patients

        doctor_ids = fetch_all_ids(cursor, "Doctor")
        patient_data = fetch_ids_and_doctor_ids(cursor, "Patient")

        # # Create Python objects for doctors and patients with the fetched IDs
        doctors = [Doctor(id=i) for i in doctor_ids]
        patients = [Patient(id=i, doctor_id=d) for i, d in patient_data]
        appointments = Appointment.populate(cursor, patients, n=num_appointments)
        line_items = LineItem.populate(cursor, n=2)
        cash_payments = CashPayment.populate(cursor)
        lits = LineItemTransaction.populate(cursor)

    connection.commit()
    print("Done populating the tables!")


if __name__ == "__main__":
    connection = make_postgres_connection()
    truncate_tables(connection)
    create_tables(connection)
    populate_tables(connection)
