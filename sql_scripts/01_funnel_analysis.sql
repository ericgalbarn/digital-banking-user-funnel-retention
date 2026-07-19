WITH funnel_stages AS (
  SELECT
    COUNT(DISTINCT CASE WHEN event_name = '1_Download_App' THEN user_id END) AS step_1_download,
    COUNT(DISTINCT CASE WHEN event_name = '2_Input_OTP' THEN user_id END) AS step_2_otp,
    COUNT(DISTINCT CASE WHEN event_name = '3_Scan_CCCD' THEN user_id END) AS step_3_cccd,
    COUNT(DISTINCT CASE WHEN event_name = '4_Face_Matching' THEN user_id END) AS step_4_face,
    COUNT(DISTINCT CASE WHEN event_name = '5_Account_Created' THEN user_id END) AS step_5_success
  FROM
    `digibank_data.fact_user_events`
)

SELECT
  step_1_download AS download_app,
  step_2_otp AS input_otp,
  step_3_cccd AS scan_cccd,
  step_4_face AS face_matching,
  step_5_success AS account_created,
  ROUND((step_5_success / step_1_download) * 100, 2) AS overall_conversion_rate,
  ROUND(((step_1_download - step_2_otp) / step_1_download) * 100, 2) AS drop_otp_pct,
  ROUND(((step_2_otp - step_3_cccd) / step_2_otp) * 100, 2) AS drop_cccd_pct,
  ROUND(((step_3_cccd - step_4_face) / step_3_cccd) * 100, 2) AS drop_face_pct,
  ROUND(((step_4_face - step_5_success) / step_4_face) * 100, 2) AS drop_success_pct
FROM
  funnel_stages;