import os

import pymysql

from config import make_mysql_connection
from factories import AppointmentFactory, DoctorFactory, LineItemFactory, PatientFactory
from models import Doctor, Patient, Appointment


def truncate_tables(connection):
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("DROP TABLE IF EXISTS Appointment;")
        cursor.execute("DROP TABLE IF EXISTS Patient;")
        cursor.execute("DROP TABLE IF EXISTS Doctor;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")


def create_tables(connection):
    with connection.cursor() as cursor:
        DoctorFactory.create_table(cursor)
        PatientFactory.create_table(cursor)
        Appointment.create_table(cursor)
    connection.commit()


def count_rows_in_tables(cursor):
    tables = ["Doctor", "Patient", "Appointment"]  # Add other tables as needed
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        count = cursor.fetchone()[0]
        print(f"The number of rows in the {table} table is {count}")


def populate_tables(connection):
    def fetch_all_ids(cursor, table_name):
        cursor.execute(f"SELECT id FROM {table_name}")
        return [row[0] for row in cursor.fetchall()]

    def fetch_ids_and_doctor_ids(cursor, table_name):
        query = f"SELECT id, doctor_id FROM {table_name}"
        cursor.execute(query)
        return [(row[0], row[1]) for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        doctors = DoctorFactory.populate(cursor, n=100)
        patients = Patient.populate(cursor, doctors, n=10)
        # Fetch IDs of inserted Doctors and Patients

        doctor_ids = fetch_all_ids(cursor, "Doctor")
        patient_data = fetch_ids_and_doctor_ids(cursor, "Patient")

        # # Create Python objects for doctors and patients with the fetched IDs
        doctors = [Doctor(id=i) for i in doctor_ids]
        patients = [Patient(id=i, doctor_id=d) for i, d in patient_data]
        appointments = Appointment.populate(cursor, patients, n=10)
        # # Populate Appointment table
        # appointments AppointmentFactory.populate(cursor, doctors, patients, n=10)

    connection.commit()
    print("Done populating the tables!")


# The rest of the code (creating tables and main execution) remains the same.


# Establishing the connection
conn = pymysql.connect(
    host=os.environ.get("MYSQL_HOST"),
    user=os.environ.get("MYSQL_USER"),
    password=os.environ.get("MYSQL_PASSWORD"),
    db=os.environ.get("MYSQL_DB"),
)

if __name__ == "__main__":
    connection = make_mysql_connection()
    truncate_tables(connection)
    create_tables(connection)
    populate_tables(connection)
