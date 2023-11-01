from datetime import datetime
from random import choice, randint

from faker import Faker

fake = Faker()

tables = [
    "doctor",
    "patient",
    "office",
    "appointment",
    "cashpayment",
    "lineitem",
    "lineitemtransaction",
]


class Doctor:
    def __init__(self, id, name=None):
        self.id = id
        self.name = name


class Patient:
    def __init__(self, name=None, age=None, doctor_id=None, id=None):
        self.id = id or None
        self.name = name or fake.name()
        self.age = age or fake.random_int(min=18, max=99)
        self.doctor_id = doctor_id or None

    @classmethod
    def populate(cls, cursor, doctors, n=1):
        print(f"Populating the {cls.__name__} table...")
        patients = [cls(doctor_id=doctor.id) for doctor in doctors for _ in range(n)]
        last_ids = []
        for patient in patients:
            cursor.execute(
                """
                INSERT INTO patient (name, age, doctor_id)
                VALUES (%s, %s, %s) RETURNING id
                """,
                (patient.name, patient.age, patient.doctor_id),
            )
            last_id = cursor.fetchone()[0]
            last_ids.append(last_id)
            patient.id = last_id
        return patients


class Office:
    def __init__(self, name=None, doctor_id=None, id=None):
        self.id = id or None
        self.name = name or fake.company()
        self.doctor_id = doctor_id

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS office (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                doctor_id INT,
                FOREIGN KEY (doctor_id) REFERENCES doctor(id)
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
                """
                INSERT INTO office (name, doctor_id)
                VALUES (%s, %s) RETURNING id
                """,
                (office.name, office.doctor_id),
            )
            last_id = cursor.fetchone()[0]
            last_ids.append(last_id)
            office.id = last_id
        return offices


class Appointment:
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
            for _ in range(n):
                office = choice(offices)
                appointment_tuple = (
                    patient.id,
                    bulk_dates.pop(),
                    patient.doctor_id,
                    office.id,
                )
                appointments.append(appointment_tuple)
        cursor.executemany(
            "INSERT INTO appointment (patient_id, date, doctor_id, office_id) VALUES (%s, %s, %s, %s)",
            appointments,
        )
        

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointment (
                id SERIAL PRIMARY KEY,
                patient_id INT,
                date DATE,
                doctor_id INT,
                office_id INT,
                FOREIGN KEY (patient_id) REFERENCES patient(id),
                FOREIGN KEY (doctor_id) REFERENCES doctor(id),
                FOREIGN KEY (office_id) REFERENCES office(id)
            );
        """
        )


class LineItem:
    def __init__(self, created_at, amount, description, appointment_id):
        self.created_at = created_at
        self.billed = amount
        self.description = description
        self.appointment_id = appointment_id

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS lineitem (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ,
            billed NUMERIC(10, 2),
            description TEXT,
            appointment_id INT,
            FOREIGN KEY (appointment_id) REFERENCES appointment(id)
        );
        """
        )

    @classmethod
    def populate(cls, cursor, n=1):
        print(f"Populating the {cls.__name__} table...")
        cursor.execute("SELECT id FROM appointment;")
        appointment_ids = [row[0] for row in cursor.fetchall()]
        line_items = []
        for appointment_id in appointment_ids:
            for _ in range(n):
                line_item_tuple = (
                    datetime.now(),
                    randint(10, 500),
                    f"Line item for appointment {appointment_id}",
                    appointment_id,
                )
                line_items.append(line_item_tuple)

        cursor.executemany(
            "INSERT INTO lineitem (created_at, billed, description, appointment_id) VALUES (%s, %s, %s, %s)",
            line_items,
        )


# New models
class CashPayment:
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
            """
            CREATE TABLE IF NOT EXISTS cashpayment (
                id SERIAL PRIMARY KEY,
                amount NUMERIC(10, 2),
                payment_method TEXT,
                created_at TIMESTAMPTZ,
                patient_id INT,
                doctor_id INT,
                line_item_id INT,
                FOREIGN KEY (patient_id) REFERENCES patient(id),
                FOREIGN KEY (doctor_id) REFERENCES doctor(id),
                FOREIGN KEY (line_item_id) REFERENCES lineitem(id)
            );
            """
        )

    @classmethod
    def populate(cls, cursor, n=1):
        print(f"Populating the {cls.__name__} table...")

        query = """
        SELECT l.id, a.patient_id, a.doctor_id 
        FROM lineitem l
        JOIN appointment a ON (l.appointment_id = a.id);
        """
        cursor.execute(query)
        line_item_data = cursor.fetchall()
        payment_methods = ["Credit Card", "Cash", "Check"]

        cash_payments = []
        for line_item_id, patient_id, doctor_id in line_item_data:
            for _ in range(n):
                cash_payment_tuple = (
                    randint(100, 500),
                    choice(payment_methods),
                    datetime.now(),
                    patient_id,
                    doctor_id,
                    line_item_id,
                )
                cash_payments.append(cash_payment_tuple)

        cursor.executemany(
            "INSERT INTO cashpayment (amount, payment_method, created_at, patient_id, doctor_id, line_item_id) VALUES (%s, %s, %s, %s, %s, %s)",
            cash_payments,
        )


class LineItemTransaction:
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
            """
            CREATE TABLE IF NOT EXISTS lineitemtransaction (
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
                FOREIGN KEY (appointment_id) REFERENCES appointment(id),
                FOREIGN KEY (doctor_id) REFERENCES doctor(id),
                FOREIGN KEY (patient_id) REFERENCES patient(id),
                FOREIGN KEY (line_item_id) REFERENCES lineitem(id)
            );
            """
        )

    @classmethod
    def populate(cls, cursor, n=1):
        print(f"Populating the {cls.__name__} table...")

        # Query the database to get lineitem details
        line_item_query = """
        SELECT l.id, l.appointment_id, a.doctor_id, a.patient_id
        FROM lineitem l
        JOIN appointment a ON (l.appointment_id = a.id);
        """
        cursor.execute(line_item_query)
        line_item_data = cursor.fetchall()

        claim_statuses = ["Pending", "Paid", "Rejected"]
        adjustment_reasons = ["-3", "-2", "-1", "1", "2"]

        line_item_transactions = []
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
                    datetime.now().date(),
                    adjustment,
                    ins_paid,
                    randint(1, 5),
                    adjustment_reason,
                    datetime.now(),
                    appointment_id,
                    doctor_id,
                    patient_id,
                    line_item_id,
                )

                line_item_transactions.append(line_item_transaction_tuple)

        cursor.executemany(
            """INSERT INTO LineItemTransaction (
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
