from models import CashPayment, LineItem

ds_pp_creation_sql = f"""CREATE MATERIALIZED VIEW public.daysheet_patientpayments_mv
AS
SELECT 
    bcp.id,
    bcp.created_at,
    bcp.amount,
    bcp.doctor_id,
    bcp.patient_id, 
    bli.description as code
FROM {CashPayment.TABLE_NAME} bcp 
JOIN {LineItem.TABLE_NAME} bli ON (bcp.line_item_id = bli.id)
WHERE bcp.amount <>0;
"""

ds_pp_index_sql = (
    """CREATE INDEX ds_pp_mv_index ON public.daysheet_patientpayments_mv (doctor_id);"""
)
