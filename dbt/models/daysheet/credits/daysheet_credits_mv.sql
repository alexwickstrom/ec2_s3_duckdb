{{ config(
    materialized = 'table',
    on_configuration_change = 'apply',
) }}

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
    lit.adjustment_reason,
    ca.office_id,
    pt.name as patient_name,
    co.name as office_name,
    cd.name as doctor_name
FROM {{ source('chronometer_production', 'billing_lineitemtransaction') }} lit
JOIN {{ source('chronometer_production', 'chronometer_appointment') }} ca ON (lit.appointment_id = ca.id)
JOIN {{ source('chronometer_production', 'chronometer_patient') }} pt ON (ca.patient_id = pt.id)
JOIN {{ source('chronometer_production', 'chronometer_office') }} co ON (ca.office_id = co.id)
JOIN {{ source('chronometer_production', 'chronometer_doctor') }} cd ON (cd.id = ca.doctor_id)
WHERE 
    lit.ins_paid <> 0 
    OR lit.adjustment_reason in ('1', '2')
