# Data Dictionary - Digital Banking Analytics Dataset

This document provides a detailed description of the tables, fields, data types, and structural relationships designed for the **Digital Banking User Journey & Retention Optimization** project.

## 📐 Data Model Overview

The dataset is structured using a **Star Schema** optimized for analytical processing (OLAP). It consists of two Fact tables tracking user activities and two Dimension tables providing contextual attributes.

---

## 1. Table: `Dim_User`

- **Description:** Contains demographic and device profiles for all users who downloaded the application. Each user has exactly **one unique record** in this table.
- **Type:** Dimension Table


| Column Name            | Data Type     | Primary/Foreign Key | Description / Allowed Values                                                                                   |
| ---------------------- | ------------- | ------------------- | -------------------------------------------------------------------------------------------------------------- |
| `user_id`              | `VARCHAR(10)` | **Primary Key**     | Unique identifier for each user (e.g., `USR00001`).                                                            |
| `age`                  | `INTEGER`     | -                   | Age of the user at registration (Range: 18 - 60).                                                              |
| `gender`               | `VARCHAR(10)` | -                   | Gender of the user (`Male`, `Female`).                                                                         |
| `device_os`            | `VARCHAR(10)` | -                   | Mobile operating system (`iOS`, `Android`).                                                                    |
| `device_model`         | `VARCHAR(50)` | -                   | Specific smartphone model (e.g., `iPhone 15`, `Samsung S24`, `Oppo A58`).                                      |
| `location`             | `VARCHAR(50)` | -                   | Geographical region (`Hanoi`, `HCM`, `Danang`, `Others`).                                                      |
| `account_created_date` | `DATE`        | -                   | The date when the user successfully completed eKYC. Contains `NULL` if the user dropped out before completion. |


---



## 2. Table: `Fact_User_Events`

- **Description:** Logs granular digital onboarding checkpoints chronologically. Users who attempt registration generate **multiple records** corresponding to their progression.
- **Type:** Fact Table


| Column Name  | Data Type     | Primary/Foreign Key | Description / Allowed Values                                                                                                    |
| ------------ | ------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `event_id`   | `VARCHAR(15)` | **Primary Key**     | Unique identifier for each event log (e.g., `EVT0000001`).                                                                      |
| `user_id`    | `VARCHAR(10)` | **Foreign Key**     | References `Dim_User(user_id)`.                                                                                                 |
| `event_name` | `VARCHAR(30)` | -                   | Name of the onboarding stage: 1. `1_Download_App` 2. `2_Input_OTP` 3. `3_Scan_CCCD` 4. `4_Face_Matching` 5. `5_Account_Created` |
| `timestamp`  | `TIMESTAMP`   | -                   | Precise date and time of the event occurrence (Range: Jan 2026 - Jun 2026).                                                     |


---



## 3. Table: `Fact_Transactions`

- **Description:** Records all financial activities performed by users **after** successful account activation (`5_Account_Created`). 
- **Type:** Fact Table


| Column Name           | Data Type       | Primary/Foreign Key | Description / Allowed Values                                            |
| --------------------- | --------------- | ------------------- | ----------------------------------------------------------------------- |
| `transaction_id`      | `VARCHAR(15)`   | **Primary Key**     | Unique transaction identifier (e.g., `TX20260000001`).                  |
| `user_id`             | `VARCHAR(10)`   | **Foreign Key**     | References `Dim_User(user_id)`.                                         |
| `transaction_type_id` | `VARCHAR(10)`   | **Foreign Key**     | References `Dim_Transaction_Type(transaction_type_id)`.                 |
| `amount`              | `DECIMAL(15,2)` | -                   | Monetary value of the transaction in VND (Range: 10,000 to 50,000,000). |
| `transaction_date`    | `DATE`          | -                   | Date of transaction. Must be $\ge$ `Dim_User(account_created_date)`.    |


---



## 4. Table: `Dim_Transaction_Type`

- **Description:** A metadata lookup table defining financial transaction categories supported on the digital banking application.
- **Type:** Dimension Table (Lookup)


| Column Name             | Data Type     | Primary/Foreign Key | Description / Allowed Values                                                                                                  |
| ----------------------- | ------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `transaction_type_id`   | `VARCHAR(10)` | **Primary Key**     | Unique category code (e.g., `TX_TRF`, `TX_QR`, `TX_SAV`).                                                                     |
| `transaction_type_name` | `VARCHAR(50)` | -                   | Human-readable name: - `Chuyen_Tien` (Fund Transfer) - `Quet_QR_Pay` (QR Code Payment) - `Gui_Tiet_Kiem_So` (Digital Savings) |


---



## 🧠 Business Logic & Data Anomalies (Injected Insights)

To simulate real-world data challenges and test analytical integrity, the following rules are systematically embedded during generation:

1. **eKYC Friction Bias:** Users with `device_os = 'Android'` and budget `device_model` (e.g., `Oppo A58`) are assigned a **35% higher failure rate** at the `3_Scan_CCCD` stage due to simulated camera integration limits.
2. **Retention Correlation:** Users who trigger at least one `TX_SAV` (Digital Savings) transaction within their first 7 days are mapped to a **higher dynamic probability matrix** for subsequent transactions, modeling strong product activation signals.

