from datetime import datetime
from random import choice, randint

from config import BASE_SCHEMA, tables
from faker import Faker
from psycopg2 import sql

fake = Faker()


class Doctor:
    TABLE_NAME = f"{BASE_SCHEMA}.doctor"

    def __init__(self, id=None, name=None):
        self.id = id or None
        self.name = name

    @classmethod
    def create_table(cls, cursor):
        print(f"Creating {cls.TABLE_NAME}")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BASE_SCHEMA}.doctor (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255)
            );
        """
        )

    @classmethod
    def populate(cls, cursor, n=1):
        print("Populating the Doctor table")
        doctors = [cls(name=fake.name()) for i in range(n)]
        for doctor in doctors:
            cursor.execute(
                f"INSERT INTO {BASE_SCHEMA}.doctor (name) VALUES (%s) RETURNING id",
                (doctor.name,),
            )
            doctor_id = cursor.fetchone()[0]
            doctor.id = doctor_id
        return doctors


class Patient:
    TABLE_NAME = f"{BASE_SCHEMA}.patient"

    def __init__(self, name=None, age=None, doctor_id=None, id=None):
        self.id = id or None
        self.name = name or fake.name()
        self.age = age or fake.random_int(min=18, max=99)
        self.doctor_id = doctor_id or None

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                age INT,
                doctor_id INT,
                FOREIGN KEY (doctor_id) REFERENCES {BASE_SCHEMA}.doctor(id)
            );"""
        )

    @classmethod
    def populate(cls, cursor, doctors, n=1):
        print(f"Populating the {cls.__name__} table...")
        schema_name, table_name = cls.TABLE_NAME.split(".")

        patients = [cls(doctor_id=doctor.id) for doctor in doctors for _ in range(n)]
        last_ids = []
        for patient in patients:
            query = sql.SQL(
                """
                INSERT INTO {}.{} (name, age, doctor_id)
                VALUES (%s, %s, %s) RETURNING id
                """
            ).format(sql.Identifier(schema_name), sql.Identifier(table_name))
            cursor.execute(
                query,
                (patient.name, patient.age, patient.doctor_id),
            )
            last_id = cursor.fetchone()[0]
            last_ids.append(last_id)
            patient.id = last_id
        return patients


class Office:
    TABLE_NAME = f'"{BASE_SCHEMA}"."office"'

    def __init__(self, name=None, doctor_id=None, id=None):
        self.id = id or None
        self.name = name or fake.company()
        self.doctor_id = doctor_id

    @classmethod
    def create_table(cls, cursor):
        print(f"Creating {cls.TABLE_NAME}...")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                doctor_id INT,
                FOREIGN KEY (doctor_id) REFERENCES {Doctor.TABLE_NAME}(id)
            );
        """
        )

    @classmethod
    def populate(cls, cursor, doctors, n=1):
        print(f"Populating the {cls.__name__} table...")
        offices = [cls(doctor_id=doctor.id) for doctor in doctors for _ in range(n)]
        last_ids = []
        for office in offices:
            cursor.execute(
                f"""
                INSERT INTO {cls.TABLE_NAME} (name, doctor_id)
                VALUES (%s, %s) RETURNING id
                """,
                (office.name, office.doctor_id),
            )
            last_id = cursor.fetchone()[0]
            last_ids.append(last_id)
            office.id = last_id
        return offices


class Appointment:
    TABLE_NAME = f"{BASE_SCHEMA}.appointment"

    def __init__(self, patient_id, doctor_id, office_id, date=None):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.office_id = office_id
        self.date = date if date else Faker().date_this_decade()

    @classmethod
    def populate(cls, cursor, patients, offices, n=1):
        print(f"Populating the {cls.__name__} table...")
        faker = Faker()
        total_appointments = len(patients) * n
        bulk_dates = [faker.date_this_decade() for _ in range(total_appointments)]
        appointments = []
        for patient in patients:
            filtered_offices = [
                office for office in offices if office.doctor_id == patient.doctor_id
            ]
            for _ in range(n):
                office = choice(filtered_offices)
                appointment_tuple = (
                    patient.id,
                    bulk_dates.pop(),
                    patient.doctor_id,
                    office.id,
                )
                appointments.append(appointment_tuple)
        query = f"INSERT INTO {cls.TABLE_NAME} (patient_id, date, doctor_id, office_id) VALUES (%s, %s, %s, %s)"
        print(query)
        cursor.executemany(
            query,
            appointments,
        )

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(f"SET search_path to {BASE_SCHEMA};")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BASE_SCHEMA}.appointment (
                id SERIAL PRIMARY KEY,
                patient_id INT,
                date DATE,
                doctor_id INT,
                office_id INT,
                FOREIGN KEY (patient_id) REFERENCES {BASE_SCHEMA}.patient(id),
                FOREIGN KEY (doctor_id) REFERENCES {BASE_SCHEMA}.doctor(id),
                FOREIGN KEY (office_id) REFERENCES {BASE_SCHEMA}.office(id)
            );
        """
        )


class LineItem:
    TABLE_NAME = f'"{BASE_SCHEMA}"."lineitem"'

    def __init__(self, created_at, amount, description, appointment_id):
        self.created_at = created_at
        self.billed = amount
        self.description = description
        self.appointment_id = appointment_id

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(f"SET search_path to {BASE_SCHEMA};")
        cursor.execute(
            f"""
        CREATE TABLE IF NOT EXISTS lineitem (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ,
            billed NUMERIC(10, 2),
            description TEXT,
            appointment_id INT,
            FOREIGN KEY (appointment_id) REFERENCES {BASE_SCHEMA}.appointment(id)
        );
        """
        )

    @classmethod
    def populate(cls, cursor, n=1):
        print(f"Populating the {cls.__name__} table...")
        cursor.execute(f"SELECT id FROM {Appointment.TABLE_NAME};")
        appointment_ids = [row[0] for row in cursor.fetchall()]
        line_items = []
        descriptions = [Faker().sentence(nb_words=6) for _ in range(15)]
        for appointment_id in appointment_ids:
            for _ in range(n):
                line_item_tuple = (
                    datetime.now(),  # created_at
                    randint(10, 500),  # billed
                    choice(descriptions),  # description
                    appointment_id,
                )
                line_items.append(line_item_tuple)

        cursor.executemany(
            "INSERT INTO lineitem (created_at, billed, description, appointment_id) VALUES (%s, %s, %s, %s)",
            line_items,
        )


class CashPayment:
    TABLE_NAME = f'"{BASE_SCHEMA}"."cashpayment"'

    def __init__(
        self,
        amount,
        payment_method,
        created_at,
        patient_id,
        doctor_id,
        line_item_id,
    ):
        # Initialize fields...
        self.amount = amount
        self.payment_method = payment_method
        self.created_at = created_at
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.line_item_id = line_item_id

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                amount NUMERIC(10, 2),
                payment_method TEXT,
                created_at TIMESTAMPTZ,
                patient_id INT,
                doctor_id INT,
                line_item_id INT,
                FOREIGN KEY (patient_id) REFERENCES {BASE_SCHEMA}.patient(id),
                FOREIGN KEY (doctor_id) REFERENCES {BASE_SCHEMA}.doctor(id),
                FOREIGN KEY (line_item_id) REFERENCES {BASE_SCHEMA}.lineitem(id)
            );
            """
        )

    @classmethod
    def populate(cls, cursor, n=1):
        print(f"Populating the {cls.__name__} table...")
        query = f"""
        SELECT l.id, a.patient_id, a.doctor_id 
        FROM {BASE_SCHEMA}.lineitem l
        JOIN {BASE_SCHEMA}.appointment a ON (l.appointment_id = a.id);
        """
        cursor.execute(query)
        line_item_data = cursor.fetchall()
        payment_methods = ["Credit Card", "Cash", "Check"]

        cash_payments = []
        created_at = datetime.now()
        for line_item_id, patient_id, doctor_id in line_item_data:
            for _ in range(n):
                cash_payment_tuple = (
                    randint(100, 500),
                    choice(payment_methods),
                    created_at,
                    patient_id,
                    doctor_id,
                    line_item_id,
                )
                cash_payments.append(cash_payment_tuple)

        cursor.executemany(
            f"INSERT INTO {BASE_SCHEMA}.cashpayment (amount, payment_method, created_at, patient_id, doctor_id, line_item_id) VALUES (%s, %s, %s, %s, %s, %s)",
            cash_payments,
        )


class LineItemTransaction:
    TABLE_NAME = f'"{BASE_SCHEMA}"."lineitemtransaction"'

    def __init__(
        self,
        is_archived,
        claim_status,
        trace_number,
        posted_date,
        adjustment,
        ins_paid,
        ins_idx,
        adjustment_reason,
        created_at,
        appointment_id,
        doctor_id,
        patient_id,
        line_item_id,
    ):
        # Initialize fields...
        pass

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {cls.TABLE_NAME} (
                id SERIAL PRIMARY KEY,
                is_archived BOOLEAN,
                claim_status TEXT,
                trace_number TEXT,
                posted_date DATE,
                adjustment NUMERIC(10, 2),
                ins_paid NUMERIC(10, 2),
                ins_idx INT,
                adjustment_reason INT,
                created_at TIMESTAMPTZ,
                appointment_id INT,
                doctor_id INT,
                patient_id INT,
                line_item_id INT,
                FOREIGN KEY (appointment_id) REFERENCES {Appointment.TABLE_NAME}(id),
                FOREIGN KEY (doctor_id) REFERENCES {Doctor.TABLE_NAME}(id),
                FOREIGN KEY (patient_id) REFERENCES {Patient.TABLE_NAME}(id),
                FOREIGN KEY (line_item_id) REFERENCES {LineItem.TABLE_NAME}(id)
            );
            """
        )

    @classmethod
    def populate(cls, cursor, n=1):
        print(f"Populating the {cls.__name__} table...")

        # Query the database to get lineitem details
        line_item_query = f"""
        SELECT l.id, l.appointment_id, a.doctor_id, a.patient_id
        FROM {LineItem.TABLE_NAME} l
        JOIN {Appointment.TABLE_NAME} a ON (l.appointment_id = a.id);
        """
        cursor.execute(line_item_query)
        line_item_data = cursor.fetchall()

        claim_statuses = ["Pending", "Paid", "Rejected"]
        adjustment_reasons = ["-3", "-2", "-1", "1", "2"]

        line_item_transactions = []
        now = datetime.now()
        now_date = now.date()
        for line_item_id, appointment_id, doctor_id, patient_id in line_item_data:
            for _ in range(n):
                is_credit = choice([True, False])
                ins_paid = randint(50, 200) if is_credit else 0
                adjustment = 0 if is_credit else randint(1, 50)
                adjustment_reason = None if is_credit else choice(adjustment_reasons)

                line_item_transaction_tuple = (
                    choice([True, False]),
                    choice(claim_statuses),
                    f"{randint(1000, 9999)}-{randint(1000, 9999)}",
                    now_date,
                    adjustment,
                    ins_paid,
                    randint(1, 5),
                    adjustment_reason,
                    now,
                    appointment_id,
                    doctor_id,
                    patient_id,
                    line_item_id,
                )

                line_item_transactions.append(line_item_transaction_tuple)

        cursor.executemany(
            f"""INSERT INTO {cls.TABLE_NAME} (
                is_archived, 
                claim_status, 
                trace_number, 
                posted_date, 
                adjustment, 
                ins_paid, 
                ins_idx, 
                adjustment_reason, 
                created_at, 
                appointment_id, 
                doctor_id, 
                patient_id, 
                line_item_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            line_item_transactions,
        )
