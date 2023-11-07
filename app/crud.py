from config import (
    BASE_SCHEMA,
    assert_tables,
    make_postgres_connection,
    print_tables_in_schema,
    set_up_schemas,
    truncate_tables,
    vacuum,
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


def populate_tables(connection, num_doctors=500, num_patients=12, num_appointments=10):
    def fetch_all_ids(cursor, table_class):
        assert hasattr(table_class, "TABLE_NAME")
        cursor.execute(f"SELECT id FROM {table_class.TABLE_NAME}")
        return [row[0] for row in cursor.fetchall()]

    def fetch_ids_and_doctor_ids(cursor, table_class):
        assert hasattr(table_class, "TABLE_NAME")
        query = f"SELECT id, doctor_id FROM {table_class.TABLE_NAME}"
        cursor.execute(query)
        return [(row[0], row[1]) for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        doctors = Doctor.populate(cursor, n=num_doctors)
        offices = Office.populate(cursor, doctors, n=5)
        patients = Patient.populate(cursor, doctors, n=num_patients)

        # Fetch IDs of inserted Doctors, Offices, and Patients
        doctor_ids = fetch_all_ids(cursor, Doctor)
        office_data = fetch_ids_and_doctor_ids(cursor, Office)
        patient_data = fetch_ids_and_doctor_ids(cursor, Patient)

        # Create Python objects for doctors, offices, and patients with the fetched IDs
        doctors = [Doctor(id=i) for i in doctor_ids]
        offices = [Office(id=i, doctor_id=d) for i, d in office_data]
        patients = [Patient(id=i, doctor_id=d) for i, d in patient_data]
        connection.commit()

    with connection.cursor() as cursor:
        # ... [existing code] ...

        # Start transaction
        connection.autocommit = False
        try:
            Appointment.populate(cursor, patients, offices, n=num_appointments)
            LineItem.populate(cursor, n=2)
            CashPayment.populate(cursor)
            LineItemTransaction.populate(cursor)

            # Commit all changes at once
            print("Committing all changes...")
            connection.commit()
        except Exception as e:
            # If an error occurs, rollback the transaction
            connection.rollback()
            raise e
        finally:
            # Restore the default autocommit state
            connection.autocommit = True

        count_rows_in_tables(cursor)
        vacuum(conn=connection, table_name=LineItem.TABLE_NAME)

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
    # truncate_tables(connection)
    # create_tables(connection)
    # print_tables_in_schema(connection)
    # assert_tables(connection, table_classes)
    populate_tables(connection, num_doctors=50)  # start small just to test every table
    make_mvs(connection)
    # populate_tables(connection, num_doctors=490)
