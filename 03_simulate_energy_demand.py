import pandas as pd

# --- CONFIGURATION ---
INPUT_CSV = './data/projected_stock_2030.csv'
OUTPUT_CSV = './data/simulation_results_2030.csv'

def run():
    print("\n--- STEP 3: SIMULATE ENERGY (GWh) & POWER (MW) DEMAND ---")

    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV}. Run Step 1 first.")
        return

    # 1. Technical Vehicle & Charging Assumptions
    # [Distance(km), Efficiency(kWh/km), Charger Power(kW), Coincidence Factor, Active Days]
    specs = {
        'Motorcycles':  {'km': 100, 'eff': 0.04, 'kw': 0.5,  'cf': 0.3, 'days': 350},
        'Tuk Tuks':     {'km': 100, 'eff': 0.10, 'kw': 2.0,  'cf': 0.3, 'days': 350},
        'Buses':        {'km': 250, 'eff': 1.20, 'kw': 40.0, 'cf': 0.8, 'days': 330},
        'Matatu_Std':   {'km': 200, 'eff': 0.50, 'kw': 7.0,  'cf': 0.5, 'days': 330},
        'Matatu_Rapid': {'km': 250, 'eff': 0.50, 'kw': 40.0, 'cf': 0.8, 'days': 330}
    }

    # 2. Energy and Power Calculation Engine
    def calc_for_scenario(row, scenario_col):
        cls = row['Vehicle_Type']
        n_total = row[scenario_col]
        energy_kwh, peak_kw = 0, 0

        if cls == 'Matatus':
            n_std = int(n_total * 0.8)
            n_rap = int(n_total * 0.2)

            s = specs['Matatu_Std']
            energy_kwh += n_std * s['km'] * s['eff'] * s['days']
            peak_kw    += n_std * s['kw'] * s['cf']

            r = specs['Matatu_Rapid']
            energy_kwh += n_rap * r['km'] * r['eff'] * r['days']
            peak_kw    += n_rap * r['kw'] * r['cf']

        elif cls in specs:
            s = specs[cls]
            energy_kwh += n_total * s['km'] * s['eff'] * s['days']
            peak_kw    += n_total * s['kw'] * s['cf']

        return pd.Series([energy_kwh, peak_kw])

    # 3. Execute calculations
    df[['Energy_kWh_BAU', 'Peak_kW_BAU']] = df.apply(lambda x: calc_for_scenario(x, 'EVs_BAU_2030'), axis=1)
    df[['Energy_kWh_Policy', 'Peak_kW_Policy']] = df.apply(lambda x: calc_for_scenario(x, 'EVs_Policy_2030'), axis=1)
    df[['Energy_kWh_HighAmbition', 'Peak_kW_HighAmbition']] = df.apply(lambda x: calc_for_scenario(x, 'EVs_HighAmbition_2030'), axis=1)

    df.to_csv(OUTPUT_CSV, index=False)
    print(f" > Successfully saved simulation results to: {OUTPUT_CSV}")

if __name__ == "__main__":
    run()
