from models import Appointment, Doctor, LineItemTransaction, Office, Patient

ds_credits_creation_sql = f"""CREATE MATERIALIZED VIEW public.daysheet_credits_adjustments_mv 
AS
SELECT 
    lit.id,
    lit.adjustment,
    lit.ins_paid,
    lit.ins_idx,
    lit.created_at,
    lit.appointment_id,
    lit.posted_date,
    lit.doctor_id,
    lit.patient_id,
    ca.office_id,
    pt.name as patient_name,
    co.name as office_name,
    cd.name as doctor_name
FROM {LineItemTransaction.TABLE_NAME} lit
JOIN {Appointment.TABLE_NAME} ca ON (lit.appointment_id = ca.id)
JOIN {Patient.TABLE_NAME} pt ON (ca.patient_id = pt.id)
JOIN {Office.TABLE_NAME} co ON (ca.office_id = co.id)
JOIN {Doctor.TABLE_NAME} cd ON (cd.id = ca.doctor_id)
WHERE 
    lit.ins_paid <> 0 
    OR lit.adjustment_reason in ('1', '2')
;
"""
