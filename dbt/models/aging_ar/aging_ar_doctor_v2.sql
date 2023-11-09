{{ config(MATERIALIZED='table', dist="even") }}

SELECT
    blit.doctor_id
  , dd.name                                AS doctor_name
  , (CASE
         WHEN DATE_PART( 'day', CURRENT_DATE::TIMESTAMP - ca.first_billed_date::TIMESTAMP ) <= 30
             THEN 'a. 0-30 days'
         WHEN DATE_PART( 'day', CURRENT_DATE::TIMESTAMP - ca.first_billed_date::TIMESTAMP ) <= 60
             THEN 'b. 31-60 days'
         WHEN DATE_PART( 'day', CURRENT_DATE::TIMESTAMP - ca.first_billed_date::TIMESTAMP ) <= 90
             THEN 'c. 61-90 days'
         WHEN DATE_PART( 'day', CURRENT_DATE::TIMESTAMP - ca.first_billed_date::TIMESTAMP ) <= 120
             THEN 'd. 91-120 days'
             ELSE 'e. 121+ days'
     END)                                  AS ar_bucket
  , NULLIF( SUM( blit.balance_pt * 1 ), NULL )  AS patient_ar
  , NULLIF( SUM( blit.balance_ins * 1 ), NULL ) AS insurance_ar
FROM {{ source('chronometer_production','billing_billinglineitem') }} bli
LEFT JOIN {{ source('chronometer_production','chronometer_appointment') }} ca
          ON ca.id = bli.appointment_id
LEFT JOIN {{ source('chronometer_production','billing_lineitemtransaction') }} blit
          ON blit.line_item_id = bli.id
LEFT JOIN {{ source('chronometer_production','billing_cashpayment') }} bcp
          ON bcp.line_item_id = bli.id
JOIN {{ source('chronometer_production','chronometer_doctor') }} dd
     ON blit.doctor_id = dd.id
GROUP BY 1, 2, 3


