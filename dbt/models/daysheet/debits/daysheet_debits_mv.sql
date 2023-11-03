{{ config(
    materialized = 'view',
    on_configuration_change = 'apply',
) }}

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
FROM {{ source('chronometer_production', 'lineitem') }} bli
JOIN {{ source('chronometer_production', 'appointment') }} ca 
    ON (bli.appointment_id = ca.id)
JOIN {{ source('chronometer_production', 'doctor') }} cd 
    ON (ca.doctor_id = cd.id)
JOIN {{ source('chronometer_production', 'patient') }} cp 
    ON (ca.patient_id = cp.id)