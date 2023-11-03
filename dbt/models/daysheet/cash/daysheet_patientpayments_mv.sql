{{ config(
    materialized = 'view',
    on_configuration_change = 'apply',
) }}
SELECT 
    bcp.id,
    bcp.created_at,
    bcp.amount,
    bcp.doctor_id,
    bcp.patient_id, 
    bli.description as code
FROM {{ source('chronometer_production','cashpayment') }} bcp  
JOIN {LineItem {{ source('chronometer_production','lineitem') }} bli ON (bcp.line_item_id = bli.id)
WHERE bcp.amount <>0