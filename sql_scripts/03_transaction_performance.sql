-- Project: Digital Banking User Funnel & Retention Optimization
-- Script: 03_transaction_performance.sql
-- Description: Analyzes core financial metrics and active transacting user rates for newly onboarded users.

WITH successfully_created_users AS (
  -- Step 1: Filter users who successfully completed the eKYC funnel and created an account
  SELECT DISTINCT 
    user_id
  FROM 
    `digibank_data.fact_user_events`
  WHERE 
    event_name = '5_Account_Created'
),

user_transaction_summary AS (
  -- Step 2: Aggregate transaction metrics from the financial log table
  SELECT
    user_id,
    COUNT(transaction_id) AS total_txns,
    SUM(amount) AS total_amount
  FROM
    `digibank_data.fact_transactions`
  GROUP BY
    1
)

-- Step 3: Combine eKYC results with financial logs to calculate business performance metrics
SELECT
  -- Total users who successfully opened an account
  COUNT(DISTINCT u.user_id) AS total_onboarded_users,
  
  -- Count users who made at least 1 transaction
  COUNT(DISTINCT CASE WHEN t.total_txns > 0 THEN u.user_id END) AS total_active_transacting_users,
  
  -- Safe handling of active user rate division
  COALESCE(ROUND(SAFE_DIVIDE(COUNT(DISTINCT CASE WHEN t.total_txns > 0 THEN u.user_id END), COUNT(DISTINCT u.user_id)) * 100, 2), 0) AS active_transacting_user_rate_pct,
  
  -- High-level financial volume metrics
  COALESCE(SUM(t.total_txns), 0) AS total_executed_transactions,
  COALESCE(ROUND(SUM(t.total_amount), 2), 0) AS total_transaction_volume,
  
  -- Safe handling of average transaction value division
  COALESCE(ROUND(SAFE_DIVIDE(SUM(t.total_amount), SUM(t.total_txns)), 2), 0) AS average_transaction_value
FROM
  successfully_created_users u
LEFT JOIN
  user_transaction_summary t ON u.user_id = t.user_id;