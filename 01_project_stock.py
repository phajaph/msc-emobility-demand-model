import pandas as pd

# --- CONFIGURATION ---
INPUT_CSV = './data/cleaned_baseline_2024.csv'
OUTPUT_CSV = './data/projected_stock_2030.csv'

def run():
    print("\n--- STEP 1: PROJECT DEMOGRAPHIC AND EV STOCK ---")

    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV}. Please ensure data is loaded.")
        return

    # 1. Macro-Economic Parameters
    r_demo = 0.0169  # 1.69% annual demographic growth
    years = 6        # Planning horizon: 2024 to 2030

    # 2. Project Total Commercial Fleet (Baseline + Demographic Growth)
    df['Stock_2030_Total'] = (df['Count'] * ((1 + r_demo) ** years)).round(0).astype(int)

    # 3. Apply Normative EV Penetration Scenarios
    df['EVs_BAU_2030'] = (df['Stock_2030_Total'] * 0.02).round(0).astype(int)            
    df['EVs_Policy_2030'] = (df['Stock_2030_Total'] * 0.05).round(0).astype(int)         
    df['EVs_HighAmbition_2030'] = (df['Stock_2030_Total'] * 0.15).round(0).astype(int)   

    # 4. Split Matatu Fleet by Charging Regime (80% AC Depot / 20% DC Rapid)
    def split_matatu_mix(row, col):
        if row['Vehicle_Type'] == 'Matatus':
            total = row[col]
            return pd.Series([int(total * 0.8), int(total * 0.2)])
        return pd.Series([0, 0])

    df[['Matatu_Std_Count', 'Matatu_Rapid_Count']] = df.apply(
        lambda x: split_matatu_mix(x, 'EVs_HighAmbition_2030'), axis=1
    )

    df.to_csv(OUTPUT_CSV, index=False)
    print(f" > Successfully saved projections to: {OUTPUT_CSV}")

if __name__ == "__main__":
    run()
