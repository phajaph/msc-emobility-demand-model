import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
INPUT_CSV = './data/cleaned_baseline_2024.csv'
OUTPUT_CSV = './outputs/tables/annual_ev_growth_by_class_2024_2030.csv'
SAVE_PATH_FIG = './outputs/figures/Figure_4_5_Scenarios.png'

def run():
    print("\n--- STEP 2: GENERATE SCENARIO TRAJECTORIES & TABLES ---")

    # 1. Load Baseline Data
    try:
        df = pd.read_csv(INPUT_CSV)
        base_counts = df.groupby('Vehicle_Type')['Count'].sum().to_dict()
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV}.")
        return

    # 2. Parameters
    r_demo = 0.0169  
    years = np.arange(2024, 2031)
    n_years = len(years)

    scenarios = {
        'Scenario A: BAU (2%)': 0.02,
        'Scenario B: Policy-Aligned (5%)': 0.05,
        'Scenario C: High-Ambition (15%)': 0.15
    }

    # 3. Calculate Year-by-Year Progression
    records = []
    for year_idx, year in enumerate(years):
        demo_multiplier = (1 + r_demo) ** year_idx
        
        current_fleet = {}
        total_fleet = 0
        for v_type, base_val in base_counts.items():
            stock = int(round(base_val * demo_multiplier))
            current_fleet[v_type] = stock
            total_fleet += stock

        for scenario_name, target_share in scenarios.items():
            current_share = target_share * (year_idx / (n_years - 1))
            row_data = {
                'Year': year,
                'Scenario': scenario_name,
                'Total_Commercial_Fleet': total_fleet,
                'EV_Share_%': round(current_share * 100, 2)
            }
            
            total_evs = 0
            for v_type, stock in current_fleet.items():
                ev_count = int(round(stock * current_share))
                row_data[f'{v_type}_EVs'] = ev_count
                total_evs += ev_count
                
            row_data['Total_EVs'] = total_evs
            records.append(row_data)

    df_out = pd.DataFrame(records)
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f" > Saved annual growth table to: {OUTPUT_CSV}")

    # 4. Generate Trajectory Plot
    plt.figure(figsize=(10, 6))
    
    # Extract total EVs per year for plotting
    ev_bau = df_out[df_out['Scenario'] == 'Scenario A: BAU (2%)']['Total_EVs'].values
    ev_pol = df_out[df_out['Scenario'] == 'Scenario B: Policy-Aligned (5%)']['Total_EVs'].values
    ev_amb = df_out[df_out['Scenario'] == 'Scenario C: High-Ambition (15%)']['Total_EVs'].values

    plt.plot(years, ev_amb, marker='o', color='#D62728', linewidth=2.5, label='Scenario C: High-Ambition (15%)')
    plt.plot(years, ev_pol, marker='s', color='#2CA02C', linewidth=2.5, label='Scenario B: Policy-Aligned (5%)')
    plt.plot(years, ev_bau, marker='^', color='#1F77B4', linewidth=2.5, label='Scenario A: BAU (2%)')

    plt.title('Projected EV Adoption Trajectories (2024-2030)', fontsize=14, weight='bold')
    plt.ylabel('Total Electric Vehicles', fontsize=12)
    plt.xlabel('Year', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()

    # Annotations
    plt.text(2030.1, ev_amb[-1], f"{int(ev_amb[-1]):,}", va='center', color='#D62728', weight='bold')
    plt.text(2030.1, ev_pol[-1], f"{int(ev_pol[-1]):,}", va='center', color='#2CA02C', weight='bold')
    plt.text(2030.1, ev_bau[-1], f"{int(ev_bau[-1]):,}", va='center', color='#1F77B4', weight='bold')

    plt.tight_layout()
    plt.savefig(SAVE_PATH_FIG, dpi=300)
    print(f" > Saved trajectory figure to: {SAVE_PATH_FIG}")

if __name__ == "__main__":
    run()
