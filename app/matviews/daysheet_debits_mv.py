from ..models import Appointment, Doctor, LineItem, Office, Patient

ds_debits_creation_sql = f"""CREATE MATERIALIZED VIEW public.daysheet_debits_mv
AS
SELECT 
    bli.id,
    bli.created_at,
    bli.billed,
    ca.patient_id,
    cp.name as patient_name,
    ca.doctor_id,
    cd.name as doctor_name,
    bli.appointment_id,
    ca.date as appt_created_at
FROM {LineItem.TABLE_NAME} bli
JOIN {Appointment.TABLE_NAME} ca ON (bli.appointment_id = ca.id)
JOIN {Doctor.TABLE_NAME} cd ON (ca.doctor_id = cd.id)
JOIN {Patient.TABLE_NAME} cp ON (ca.patient_id = cp.id);
"""

ds_debits_index_sql = (
    """CREATE INDEX ds_debits_mv_index ON public.daysheet_debits_mv (doctor_id);"""
)
