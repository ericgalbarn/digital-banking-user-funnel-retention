-- Project: Digital Banking User Funnel & Retention Optimization
-- Script: 02_ekyc_device_deepdive.sql
-- Description: Analyzes Face Matching drop-off rates segmented by Device OS to isolate technical friction.

WITH user_os_mapping AS (
  -- Step 1: Map each user to their respective Device OS from the Dim_User table
  SELECT 
    user_id,
    device_os
  FROM 
    `digibank_data.dim_user`
),

face_matching_funnel AS (
  -- Step 2: Join events with user OS mapping to count users at critical stages per OS
  SELECT
    u.device_os,
    COUNT(DISTINCT CASE WHEN e.event_name = '3_Scan_CCCD' THEN e.user_id END) AS step_3_cccd,
    COUNT(DISTINCT CASE WHEN e.event_name = '4_Face_Matching' THEN e.user_id END) AS step_4_face
  FROM
    `digibank_data.fact_user_events` e
  JOIN
    user_os_mapping u ON e.user_id = u.user_id
  GROUP BY
    1
)

-- Step 3: Compute the exact drop-off volumes and percentages for the Face Matching stage
SELECT
  device_os,
  step_3_cccd AS users_finished_cccd,
  step_4_face AS users_finished_face,
  (step_3_cccd - step_4_face) AS face_matching_dropouts,
  ROUND(((step_3_cccd - step_4_face) / step_3_cccd) * 100, 2) AS face_matching_drop_rate_pct
FROM
  face_matching_funnel;