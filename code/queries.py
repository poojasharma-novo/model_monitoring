fpd_data = (r"""with fpd_data as (
select lending_business_id, min(created_at) as min_created_at, min(due_date) as min_due_date from "FIVETRAN_DB"."PROD_NOVO_API_PUBLIC"."LENDING_PAYMENT_SCHEDULES"
group by 1
)

,fpd_data2 as (
select a.* from "FIVETRAN_DB"."PROD_NOVO_API_PUBLIC"."LENDING_PAYMENT_SCHEDULES" a
inner join fpd_data b
on a.lending_business_id=b.lending_business_id and a.created_at=b.min_created_at and a.due_date=b.min_due_date
)

,fpd_data3 as (
select lending_business_id, created_at, due_date, case when PAID_ON_TIME='false' then 1 else 0 end as fpd_flag from fpd_data2
where 
created_at >= date_trunc('month',current_date()) - interval '2 month'
and created_at < date_trunc('month', current_date()) - interval '1 month'
-- date(created_at) between '2023-11-01' and '2023-11-30'
and date(due_date) < date(current_date())
)


,id_mapping as (
select distinct business_id, lending_business_id
FROM FIVETRAN_DB.PROD_NOVO_API_PUBLIC.LENDING_TRANSACTIONS)

,fpd_data4 as (
select b.business_id, a.created_at, a.due_date, a.fpd_flag as true_fpd_flag
,extract('week', a.created_at) as created_at_week, month(a.created_at) as created_at_month, year(a.created_at) as created_at_year from fpd_data3 a
inner join 
id_mapping b on a.lending_business_id=b.lending_business_id
)

,approved_data as (
select json_extract_path_text(predict_meta, 'business_id') as b1_id, json_extract_path_text(predict_meta, 'data.business_id') as b2_id, 
case when b1_id is null then b2_id else b1_id end as business_id,
 COALESCE(
        json_extract_path_text(predict_meta, 'default_proba'),
        json_extract_path_text(predict_meta, 'data.default_proba'),
        null
    ) as default_proba,
novo_risk_score as rs2_score, CREATED_AT
,ROW_NUMBER() OVER(partition by business_id order by CREATED_AT desc) as row_num
from FIVETRAN_DB.PROD_NOVO_API_PUBLIC.LENDING_DECISION_RESULTS
where 1=1
and json_extract_path_text(rejection_reasons, 'data') = '[]'
and created_at >= date_trunc('month',current_date()) - interval '2 month'
  and created_at < date_trunc('month', current_date()) - interval '1 month'
-- and date(created_at) between '2023-11-01' and '2023-11-30'
)
,denied_data as (
select json_extract_path_text(predict_meta, 'business_id') as b1_id, json_extract_path_text(predict_meta, 'data.business_id') as b2_id, 
case when b1_id is null then b2_id else b1_id end as business_id,
COALESCE(
        json_extract_path_text(predict_meta, 'default_proba'),
        json_extract_path_text(predict_meta, 'data.default_proba'),
        null
    ) as default_proba,
novo_risk_score as rs2_score, CREATED_AT
,ROW_NUMBER() OVER(partition by business_id order by CREATED_AT desc) as row_num
from FIVETRAN_DB.PROD_NOVO_API_PUBLIC.LENDING_DECISION_RESULTS
where 1=1
and json_extract_path_text(rejection_reasons, 'data') != '[]'
and created_at >= date_trunc('month',current_date()) - interval '2 month'
and created_at < date_trunc('month', current_date()) - interval '1 month'
-- and date(created_at) between '2023-11-01' and '2023-11-30'
)

,denied_only_data as (
select a.* from denied_data a
left join approved_data b 
on a.business_id=b.business_id
where b.business_id is null
)

,expected_data as (
select business_id, rs2_score, created_at, default_proba, extract('week', created_at) as created_at_week, month(created_at) as created_at_month, year(created_at) as created_at_year
,'approved' as decision from approved_data where row_num=1
union
select business_id, rs2_score, created_at, default_proba,extract('week', created_at) as created_at_week, month(created_at) as created_at_month, year(created_at) as created_at_year
,'denied' as decision from denied_only_data where row_num=1
)

,expected_data_2_tmp as (
select business_id, rs2_score, default_proba, decision, created_at, created_at_year, created_at_month, created_at_week,
case 
    when rs2_score <= 461.0 then 1
    when rs2_score > 461.0 and rs2_score <= 532.2 then 2
    when rs2_score > 532.2 and rs2_score <= 582.8 then 3
    when rs2_score > 582.8 and  rs2_score <= 653.0 then 4
    when rs2_score > 653.0 then 5
end as bin,
case 
    when rs2_score < 510 then 1
    when rs2_score >= 510 then 0
    end as predicted_fpd
from expected_data
)


select a.business_id, a.rs2_score, a.default_proba, a.bin, a.decision, a.predicted_fpd, b.true_fpd_flag as actual_fpd from expected_data_2_tmp a inner join fpd_data4 b on a.business_id = b.business_id 

 """)

rs2_features = (r"""select 
-- od_count_3m
    TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'od_count_3m'),
        json_extract_path_text(predict_variables, 'data.od_count_3m'),
        json_extract_path_text(predict_variables, 'context.od_count_3m'),
        null
    )) as od_count_3m,

-- zero_balance_count_1m
    TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'zero_balance_count_1m'),
        json_extract_path_text(predict_variables, 'data.zero_balance_count_1m'), 
        json_extract_path_text(predict_variables, 'context.zero_balance_count_1m'), 
        null
    )) as zero_balance_count_1m,
                        
-- ratio_ach_credit_amt_90_180
   TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'ratio_ach_credit_amt_90_180'),
        json_extract_path_text(predict_variables, 'data.ratio_ach_credit_amt_90_180'), 
        json_extract_path_text(predict_variables, 'context.ratio_ach_credit_amt_90_180'),
        null
    )) as ratio_ach_credit_amt_90_180,
                        
 -- ratio_ach_debit_amt_90_180
   TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'ratio_ach_debit_amt_90_180'),
        json_extract_path_text(predict_variables, 'data.ratio_ach_debit_amt_90_180'), 
        json_extract_path_text(predict_variables, 'context.ratio_ach_debit_amt_90_180'), 
        null
    )) as ratio_ach_debit_amt_90_180,

-- stddev_amount_ach_c_1m
    TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'stddev_amount_ach_c_1m'),
        json_extract_path_text(predict_variables, 'data.stddev_amount_ach_c_1m'), 
        json_extract_path_text(predict_variables, 'context.stddev_amount_ach_c_1m'), 
        null
    )) as stddev_amount_ach_c_1m,
                        
-- distinct_ach_c_txns_100_6m
    TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'distinct_ach_c_txns_100_6m'),
        json_extract_path_text(predict_variables, 'data.distinct_ach_c_txns_100_6m'), 
        json_extract_path_text(predict_variables, 'context.distinct_ach_c_txns_100_6m'), 
        null
    )) as distinct_ach_c_txns_100_6m,

-- distinct_mrdc_txns_1m
    TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'distinct_mrdc_txns_1m'),
        json_extract_path_text(predict_variables, 'data.distinct_mrdc_txns_1m'), 
        json_extract_path_text(predict_variables, 'context.distinct_mrdc_txns_1m'), 
        null
    )) as distinct_mrdc_txns_1m, 

 -- ratio_debit_credit_1m
    TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'ratio_debit_credit_1m'),
        json_extract_path_text(predict_variables, 'data.ratio_debit_credit_1m'),
        json_extract_path_text(predict_variables, 'context.ratio_debit_credit_1m'), 
        null
    )) as ratio_debit_credit_1m,
                        
 -- ratio_debit_credit_3m
    TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'ratio_debit_credit_3m'),
        json_extract_path_text(predict_variables, 'data.ratio_debit_credit_3m'), 
        json_extract_path_text(predict_variables, 'context.ratio_debit_credit_3m'), 
        null
    )) as ratio_debit_credit_3m,
                        
-- median_running_balance_6m
    TO_NUMBER(COALESCE(
        json_extract_path_text(predict_variables, 'median_running_balance_6m'),
        json_extract_path_text(predict_variables, 'data.median_running_balance_6m'),
        json_extract_path_text(predict_variables, 'context.median_running_balance_6m'),
        null
    )) as median_running_balance_6m,
                                                                                  
lending_business_id, 
COALESCE(
        json_extract_path_text(predict_variables, 'business_id'),
        json_extract_path_text(predict_variables, 'data.business_id'),
        json_extract_path_text(predict_variables, 'context.business_id'),
        null
     ) as business_id,
    
 date(created_at) as created_at

FROM
    FIVETRAN_DB.PROD_NOVO_API_PUBLIC.LENDING_APPLICATION_SUBMISSION_VARIABLES

WHERE
    business_id is not null and
    created_at >= date_trunc('month',current_date()) - interval '2 month'
  and created_at < date_trunc('month', current_date()) - interval '1 month'
    -- date(created_at) between '2023-01-01' and '2023-01-31'

ORDER BY
    created_at """)
