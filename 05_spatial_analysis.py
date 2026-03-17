import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
INPUT_CSV = './data/simulation_results_2030.csv'
OUTPUT_DIR = './outputs/figures/'

def run():
    print("\n--- GENERATING NODAL SPATIAL ANALYSIS ---")

    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV}.")
        return

    scenarios = [
        ('BAU', 'Business-As-Usual (2%)'),
        ('Policy', 'Policy-Aligned (5%)'),
        ('HighAmbition', 'High-Ambition (15%)')
    ]

    for suffix, title_desc in scenarios:
        col_name = f'Peak_kW_{suffix}'
        
        if col_name not in df.columns:
            continue

        # Aggregate loads by Administrative Node
        nodal_df = df.groupby('Administrative_Unit')[col_name].sum().reset_index()
        nodal_df['MW'] = nodal_df[col_name] / 1000
        nodal_df = nodal_df.sort_values(by='MW', ascending=False)

        # Apply Topological Zoning Logic
        colors = []
        for load in nodal_df['MW']:
            if load >= 1.0: colors.append('#D62728')   # Red Zone (Critical Grid Constraint)
            elif load >= 0.5: colors.append('#FF7F0E')  # Orange Zone (Moderate Upgrade)
            else: colors.append('#2CA02C')             # Green Zone (Decentralized Accommodated)

        # Plotting
        plt.figure(figsize=(14, 7)) 
        bars = plt.bar(nodal_df['Administrative_Unit'], nodal_df['MW'], color=colors, edgecolor='black')

        plt.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, label='Grid Upgrade Threshold (1 MW)')
        plt.title(f'Nodal Peak Load Analysis - {title_desc} (2030)', fontsize=14, weight='bold')
        plt.ylabel('Coincident Peak Load (MW)', fontsize=12)
        plt.xlabel('Administrative Revenue Unit', fontsize=12)
        plt.xticks(rotation=45, ha='right') 
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.3)

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height + 0.05, f'{height:.2f}', ha='center', fontsize=10, weight='bold')

        plt.tight_layout()
        
        save_path = f'{OUTPUT_DIR}Figure_4_10_Nodal_Analysis_{suffix}.png'
        plt.savefig(save_path, dpi=300)
        print(f" > Map Saved to: {save_path}")
        
        plt.close()

if __name__ == "__main__":
    run()
