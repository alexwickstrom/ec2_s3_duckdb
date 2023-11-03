ds_debits_creation_sql = """CREATE MATERIALIZED VIEW public.daysheet_debits_mv
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
FROM lineitem bli
JOIN appointment ca ON (bli.appointment_id = ca.id)
JOIN doctor cd ON (ca.doctor_id = cd.id)
JOIN patient cp ON (ca.patient_id = cp.id);
"""

ds_debits_index_sql = (
    """CREATE INDEX ds_debits_mv_index ON public.daysheet_debits_mv (doctor_id);"""
)
