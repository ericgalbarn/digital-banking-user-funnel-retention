import csv
import random
from datetime import datetime, timedelta

# --- INITIAL CONFIGURATION & PARAMETERS ---
TOTAL_USERS = 6000  # Number of initial users downloading the app
START_DATE = datetime(2026, 1, 1)
END_DATE = datetime(2026, 6, 30)

# Demographic and Device Metadata Lookup lists
LOCATIONS = ['Hanoi', 'HCM', 'Danang', 'Others']
DEVICES = {
    'iOS': ['iPhone 15', 'iPhone 14', 'iPhone 13'],
    'Android': ['Samsung S24', 'Samsung A55', 'Oppo A58', 'Xiaomi Redmi 13']
}

# 1. GENERATE DATA FOR DIM_TRANSACTION_TYPE (Metadata Lookup Table)
def generate_dim_tx_types():
    tx_types = [
        {'transaction_type_id': 'TX_TRF', 'transaction_type_name': 'Chuyen_Tien'},
        {'transaction_type_id': 'TX_QR', 'transaction_type_name': 'Quet_QR_Pay'},
        {'transaction_type_id': 'TX_SAV', 'transaction_type_name': 'Gui_Tiet_Kiem_So'}
    ]
    with open('data/dim_transaction_type.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['transaction_type_id', 'transaction_type_name'])
        writer.writeheader()
        writer.writerows(tx_types)
    print("✓ Successfully generated data/dim_transaction_type.csv")

# 2. GENERATE MAIN DATASETS: USERS, CORE JOURNEY EVENTS, AND TRANSACTIONS
def generate_main_datasets():
    dim_users = []
    fact_user_events = []
    fact_transactions = []
    
    event_id_counter = 1
    tx_id_counter = 1
    
    # 5-stage linear digital banking onboarding funnel
    stages = ['1_Download_App', '2_Input_OTP', '3_Scan_CCCD', '4_Face_Matching', '5_Account_Created']

    for i in range(1, TOTAL_USERS + 1):
        user_id = f"USR{i:05d}"
        age = random.randint(18, 60)
        gender = random.choice(['Male', 'Female'])
        location = random.choice(LOCATIONS)
        os = random.choice(['iOS', 'Android'])
        model = random.choice(DEVICES[os])
        
        # Simulate random app download timestamps spanning across the 6-month period
        # Buffering 30 days at the end to allow cohort tracking window
        days_offset = random.randint(0, (END_DATE - START_DATE).days - 30)
        current_time = START_DATE + timedelta(days=days_offset, hours=random.randint(7, 22), minutes=random.randint(0, 59))
        
        account_created_date = ""
        is_success = True
        
        # Execute onboarding funnel simulation per individual user
        for stage in stages:
            if not is_success:
                break
                
            # Log chronological granular step events
            fact_user_events.append({
                'event_id': f"EVT{event_id_counter:07d}",
                'user_id': user_id,
                'event_name': stage,
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
            })
            event_id_counter += 1
            
            # Add realistic time gaps between screen flows (1 to 5 minutes)
            current_time += timedelta(minutes=random.randint(1, 5))
            
            # --- INJECTED SYSTEMIC BIAS: eKYC FRICTION POINT ---
            # Budget Android model (Oppo A58) is programmed with a simulated 50% failure rate at Scan CCCD step
            if stage == '3_Scan_CCCD':
                drop_prob = 0.50 if (os == 'Android' and model == 'Oppo A58') else 0.15
                if random.random() < drop_prob:
                    is_success = False
            else:
                # Baseline 5% random drop-off at other generic onboarding stages
                if random.random() < 0.05:
                    is_success = False
                    
            # If the user successfully completes the entire onboarding pipeline
            if stage == '5_Account_Created' and is_success:
                account_created_date = current_time.strftime('%Y-%m-%d')

        # Map complete user demographic profiles to Dim_User
        dim_users.append({
            'user_id': user_id,
            'age': age,
            'gender': gender,
            'device_os': os,
            'device_model': model,
            'location': location,
            'account_created_date': account_created_date
        })
        
        # --- GENERATE TRANSACTION LOGS FOR SUCCESSFULLY ONBOARDED USERS ---
        if account_created_date:
            created_dt = datetime.strptime(account_created_date, '%Y-%m-%d')
            
            # 25% base probability of early digital savings feature activation
            has_savings_early = random.random() < 0.25
            
            # --- INJECTED SYSTEMIC BIAS: COHORT RETENTION CORRELATION ---
            # Users with early savings show high product engagement stability (85% activity chance vs 40% baseline)
            active_probability = 0.85 if has_savings_early else 0.40
            
            # Simulate historical recurring transactions over subsequent months
            loop_date = created_dt
            while loop_date <= END_DATE:
                # Evaluate dynamic active state for the current tracking month block
                if loop_date != created_dt and random.random() > active_probability:
                    # Churn state for the month: Skip transaction generation
                    loop_date += timedelta(days=30)
                    continue
                    
                # Generate a cluster of 3 to 8 recurring monthly financial transactions
                tx_count = 1 if (loop_date == created_dt and has_savings_early) else random.randint(3, 8)
                for _ in range(tx_count):
                    tx_date = loop_date + timedelta(days=random.randint(0, 28))
                    if tx_date > END_DATE:
                        break
                        
                    # Handle product action assignments
                    if loop_date == created_dt and has_savings_early and _ == 0:
                        tx_type = 'TX_SAV'  # Force early activation product log
                        amount = round(random.uniform(5000000, 50000000), 2)  # High value savings deposit
                    else:
                        tx_type = random.choice(['TX_TRF', 'TX_QR'])
                        amount = round(random.uniform(10000, 2000000), 2)  # Retail standard volumes
                        
                    fact_transactions.append({
                        'transaction_id': f"TX{tx_id_counter:07d}",
                        'user_id': user_id,
                        'transaction_type_id': tx_type,
                        'amount': amount,
                        'transaction_date': tx_date.strftime('%Y-%m-%d')
                    })
                    tx_id_counter += 1
                    
                loop_date += timedelta(days=30)

    # --- SAVE STRUCTURED ARTIFACTS TO TARGET CSV DATASETS ---
    with open('data/dim_user.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'age', 'gender', 'device_os', 'device_model', 'location', 'account_created_date'])
        writer.writeheader()
        writer.writerows(dim_users)
        
    with open('data/fact_user_events.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['event_id', 'user_id', 'event_name', 'timestamp'])
        writer.writeheader()
        writer.writerows(fact_user_events)
        
    with open('data/fact_transactions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['transaction_id', 'user_id', 'transaction_type_id', 'amount', 'transaction_date'])
        writer.writeheader()
        writer.writerows(fact_transactions)

    print(f"✓ Successfully generated data/dim_user.csv ({len(dim_users)} rows)")
    print(f"✓ Successfully generated data/fact_user_events.csv ({len(fact_user_events)} rows)")
    print(f"✓ Successfully generated data/fact_transactions.csv ({len(fact_transactions)} rows)")

if __name__ == "__main__":
    generate_dim_tx_types()
    generate_main_datasets()
    print("\n🎉 MOCK DATA GENERATION COMPLETE. DATASETS EXPORTED SUCCESSFULLY!")