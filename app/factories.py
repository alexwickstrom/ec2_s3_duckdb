from factory import Factory, Faker, SubFactory

from faker import Faker as RealFaker

rfaker = RealFaker()

from models import (
    Appointment,
    CashPayment,
    Doctor,
    LineItem,
    LineItemTransaction,
    Patient,
)


class DoctorFactory(Factory):
    id = Faker("random_int", min=1, max=100)
    name = Faker("name")

    @classmethod
    def populate(cls, cursor, n=1):
        print("Populating the Doctor table")
        doctors = [cls(id=i, name=rfaker.name()) for i in range(1, n + 1)]
        values = [(doc.id, doc.name) for doc in doctors]
        try:
            cursor.executemany("INSERT INTO doctor (id, name) VALUES (%s, %s)", values)
        except Exception as e:
            cursor.execute("SELECT * FROM doctor")
            import pdb

            pdb.set_trace()
        return doctors

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS doctor (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255)
            );
        """
        )

    class Meta:
        model = Doctor


class PatientFactory:
    name = Faker("name")
    age = Faker("random_int", min=18, max=99)
    doctor_id = Faker("random_int", min=1, max=100)

    @classmethod
    def populate(cls, cursor, doctors, n=1):
        print("Populating the Patient table")
        patients = [cls(doctor_id=doctor.id) for doctor in doctors for _ in range(n)]
        values = [
            (patient.name, patient.age, patient.doctor_id) for patient in patients
        ]
        cursor.executemany(
            "INSERT INTO patient (name, age, doctor_id) VALUES (%s, %s, %s)",
            values,
        )
        return patients

    @classmethod
    def create_table(cls, cursor):
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS patient (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                age INT,
                doctor_id INT,
                FOREIGN KEY (doctor_id) REFERENCES doctor(id)
            );"""
        )

    class Meta:
        model = Patient


class AppointmentFactory(Factory):
    patient = SubFactory(PatientFactory)
    doctor_id = SubFactory(DoctorFactory)
    date = Faker("date_this_decade")

    class Meta:
        model = Appointment


class LineItemFactory(Factory):
    class Meta:
        model = LineItem

    id = Faker("random_int", min=1, max=100000)
    created_at = Faker("date_this_decade")
    amount = Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    description = Faker("sentence")
    appointment = SubFactory(AppointmentFactory)


class CashPaymentFactory(Factory):
    class Meta:
        model = CashPayment

    # Initialize fields with Faker...
    @classmethod
    def populate(cls, cursor, patient, doctor, line_item):
        cash_payment = CashPaymentFactory(
            patient=patient, doctor=doctor, line_item=line_item
        )
        cursor.execute(
            "INSERT INTO CashPayment (id, amount, payment_method, created_at, patient_id, doctor_id, line_item_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                cash_payment.id,
                cash_payment.amount,
                cash_payment.payment_method,
                cash_payment.created_at,
                cash_payment.patient_id,
                cash_payment.doctor_id,
                cash_payment.line_item_id,
            ),
        )


class LineItemTransactionFactory(Factory):
    class Meta:
        model = LineItemTransaction
