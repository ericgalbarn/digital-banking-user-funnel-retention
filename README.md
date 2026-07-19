# Digital Banking User Journey & Retention Optimization Dashboard

## 📌 Project Overview

This is an engineering-focused analytics solution built to optimize the user onboarding experience and long-term retention within **ABBank's Digital Banking platform**. By implementing **Conversion Funnel Analysis** and **Cohort Retention Analysis**, this project identifies critical bottlenecks in the digital registration (eKYC) pipeline and evaluates user loyalty over time.

---

## 📊 Business Problem & Analytics Framework

### 1. eKYC Conversion Funnel Analysis

- **The Bottleneck:** High user drop-off during digital onboarding leads to wasted Marketing Acquisition Costs (CAC).
- **The Framework:** A 5-stage linear funnel is implemented to isolate systemic friction points:

```
Download App → Input Phone/OTP → Scan CCCD (eKYC) → Face Matching → Account Created
```



### 2. Cohort Retention Analysis

- **The Problem:** Monthly Active Users (MAU) can be a vanity metric if driven purely by short-term promo campaigns while existing users quietly churn.
- **The Framework:** Time-based cohorts grouped by `Account_Created_Month` to track subsequent financial transactions (Transfers, QR Pays, Savings) from Month 0 to Month 6.

---



## 📐 Data Architecture & Schema (Star Schema)

To ensure optimal performance in Power BI, the dataset (~100,000 rows) is modeled using a **Star Schema** optimized for analytical querying (OLAP):

```
       [Dim_User]               [Dim_Date]
           |                        |
           +-----------+------------+
                       |
                       v
               [Fact_Transactions] <--- [Dim_Transaction_Type]
                       ^
                       |
               [Fact_User_Events]
```

- **Fact_User_Events:** Stores granular eKYC journey checkpoints (~30,000 rows).
- **Fact_Transactions:** Stores financial behaviors of active users (~70,000 rows).
- **Dim_User / Dim_Date:** Conformed dimensions supporting seamless slicing across funnels and cohorts.

---



## 💻 Core Technical Implementations (Code Highlights)



### 1. SQL Funnel Sequencing (Window Functions)

To build the funnel without distorting user drop-offs, event sequencing is handled using explicit conditional aggregation in SQL:

```sql
SELECT 
    event_name,
    COUNT(DISTINCT user_id) AS total_users,
    LAG(COUNT(DISTINCT user_id)) OVER (ORDER BY MIN(timestamp)) AS previous_stage_users,
    ROUND(COUNT(DISTINCT user_id) * 100.0 / FIRST_VALUE(COUNT(DISTINCT user_id)) OVER (ORDER BY MIN(timestamp)), 2) AS conversion_rate
FROM fact_user_events
GROUP BY event_name;
```



### 2. Power BI DAX for Dynamic Cohort Retention

The dynamic retention matrix handles shifting date contexts natively:

```dax
Retention % = 
VAR CurrentCohortMonth = SELECTEDVALUE('Dim_User'[CohortMonth])
VAR MonthsSubsequent = SELECTEDVALUE('Dim_Date'[MonthsSinceRegistration])
VAR ActiveUsers = 
    CALCULATE(
        DISTINCTCOUNT('Fact_Transactions'[user_id]),
        FILTER(
            'Fact_Transactions',
            RELATED('Dim_User'[CohortMonth]) = CurrentCohortMonth &&
            DATEDIFF(RELATED('Dim_User'[Account_Created_Date]), 'Fact_Transactions'[transaction_date], MONTH) = MonthsSubsequent
        )
    )
RETURN
    DIVIDE(ActiveUsers, [Cohort_Size], 0)
```

---



## 📂 Repository Structure

```
├── data/                  # Simulated datasets (Contains 4 generated CSV files, ~74k+ dynamic rows)
├── pbix_dashboard/       # Power BI Dashboard file (.pbix)
├── sql_scripts/           # Production-ready SQL scripts
└── README.md              # Project documentation
```

---

## 📈 Dataset Execution Summary & Insights



### 📊 Dataset Scale (Generated Metrics)

- **Total App Downloads (**`Dim_User`**):** 6,000 users.
- **Total Onboarding Logs (**`Fact_User_Events`**):** 25,508 events tracking the 5-stage eKYC pipeline.
- **Total Financial Logs (**`Fact_Transactions`**):** 42,567 transaction records spanning Jan 2026 - Jun 2026.



### 📌 Tab 1: eKYC Funnel Performance

- **Overall Conversion:** Only **X%** of app downloads result in a fully verified account.
- **The Friction Point:** The largest drop-off occurs at the **[Insert Step, e.g., Scan CCCD]** stage (**Y%** drop), heavily 
- skewed towards **[Insert Segment, e.g., Android Devices]**, indicating an OS-specific hardware integration bug.



### 📌 Tab 2: User Retention Heatmap

- **Month 1 Baseline:** Average Month 1 Retention stands at **A%**.
- **Churn Cliff:** A severe engagement drop-off is detected at **Month B** (**< C%**), signaling a failure in mid-funnel user re-engagement.
- **Sticky Feature:** Users engaging with **[Insert Feature, e.g., Digital Savings]** exhibit a **D×** higher Customer Lifetime Value (LTV).

---



## 💡 Data-Driven Recommendations

1. **Tech Intervention:** Deploy client-side error logging on the **[Insert Step]** screen to capture image processing failures in real time.
2. **Marketing Automation:** Trigger automated push notifications with targeted zero-fee incentives within 24 hours for users stalled post-OTP verification.
3. **Product Feature Promotion:** Re-architect the app's home screen to surface **[Insert High-Value Feature]** immediately after onboarding to lock in early user retention.

