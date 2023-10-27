from faker import Faker

fake = Faker()


class Doctor:
    def __init__(self, id, name=None):
        self.id = id
        self.name = name


class Patient:
    def __init__(self, name=None, age=None, doctor_id=None, id=None):
        self.id = id or None  # Keep as None if not provided
        self.name = name or fake.name()
        self.age = age or fake.random_int(min=18, max=99)
        self.doctor_id = doctor_id or None

    @classmethod
    def populate(cls, cursor, doctors, n=1):
        patients = [cls(doctor_id=doctor.id) for doctor in doctors for _ in range(n)]
        values = [
            (patient.name, patient.age, patient.doctor_id) for patient in patients
        ]
        cursor.executemany(
            "INSERT INTO Patient (name, age, doctor_id) VALUES (%s, %s, %s)", values,
        )
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchone()[0]
        for i, patient in enumerate(patients):
            patient.id = last_id - len(patients) + i + 1
        return patients


class Appointment:
    def __init__(self, patient_id, doctor_id, date=None):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date if date else Faker().date_this_decade()

    @classmethod
    def populate(cls, cursor, patients, n=1):
        print("Populating the Appointment table . . .")
        faker = Faker()
        total_appointments = len(patients) * n
        bulk_dates = [faker.date_this_decade() for _ in range(total_appointments)]
        date_index = 0
        for patient in patients:
            appointments = []
            for _ in range(n):
                appointment_tuple = (
                    patient.id,
                    bulk_dates[date_index],
                    patient.doctor_id,
                )
                appointments.append(appointment_tuple)
                date_index += 1
            cursor.executemany(
                "INSERT INTO Appointment (patient_id, date, doctor_id) VALUES (%s, %s, %s)",
                appointments,
            )
        return

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Appointment (
                id INT PRIMARY KEY AUTO_INCREMENT,
                patient_id INT,
                date DATE,
                doctor_id INT,
                FOREIGN KEY (patient_id) REFERENCES Patient(id),
                FOREIGN KEY (doctor_id) REFERENCES Doctor(id)
            );
        """
        )


class LineItem:
    def __init__(self, created_at, amount, description, appointment_id):
        self.created_at = created_at
        self.amount = amount
        self.description = description
        self.appointment_id = appointment_id


# New models
class CashPayment:
    def __init__(
        self, amount, payment_method, created_at, patient_id, doctor_id, line_item_id,
    ):
        # Initialize fields...
        self.amount = amount
        self.payment_method = payment_method
        self.created_at = created_at
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.line_item_id = line_item_id


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
