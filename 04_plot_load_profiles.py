import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# --- CONFIGURATION ---
INPUT_CSV = './data/simulation_results_2030.csv'
SAVE_PATH_STACK = './outputs/figures/Figure_4_8_Load_Profile.png'
SAVE_PATH_DUAL = './outputs/figures/Figure_4_9_Dual_Axis_Overlay.png'

def extract_load_components(df):
    """Extracts dynamic vehicle counts and computes peak MW requirements."""
    moto_count = df[df['Vehicle_Type'] == 'Motorcycles']['EVs_HighAmbition_2030'].sum()
    tuk_count = df[df['Vehicle_Type'] == 'Tuk Tuks']['EVs_HighAmbition_2030'].sum()
    micro_peak_mw = ((moto_count * 0.5 * 0.3) + (tuk_count * 2.0 * 0.3)) / 1000

    matatu_total = df[df['Vehicle_Type'] == 'Matatus']['EVs_HighAmbition_2030'].sum()
    std_matatu_peak_mw = ((matatu_total * 0.8) * 7.0 * 0.5) / 1000
    rapid_matatu_peak_mw = ((matatu_total * 0.2) * 40.0 * 0.8) / 1000

    bus_count = df[df['Vehicle_Type'] == 'Buses']['EVs_HighAmbition_2030'].sum()
    bus_peak_mw = (bus_count * 40.0 * 0.8) / 1000

    return micro_peak_mw, std_matatu_peak_mw, rapid_matatu_peak_mw, bus_peak_mw

def gaussian(x, mu, sig, peak):
    """Generates synthetic hourly load distribution curves."""
    return peak * np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

def run():
    print("\n--- GENERATING SPATIO-TEMPORAL LOAD PROFILES ---")
    
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV}. Run simulations first.")
        return

    micro_mw, std_matatu_mw, rapid_matatu_mw, bus_mw = extract_load_components(df)

    hours = np.linspace(0, 24, 200)

    # Construct EV Load Curves
    micro_load = gaussian(hours, 13, 1.5, micro_mw * 0.57) + gaussian(hours, 19, 2.0, micro_mw * 0.43)
    std_matatu_load = gaussian(hours, 3, 2.5, std_matatu_mw) + gaussian(hours, 27, 2.5, std_matatu_mw) + gaussian(hours, -21, 2.5, std_matatu_mw)
    bus_load = gaussian(hours, 2, 1.5, bus_mw) + gaussian(hours, 26, 1.5, bus_mw) + gaussian(hours, -22, 1.5, bus_mw)
    rapid_matatu_load = gaussian(hours, 13, 1.8, rapid_matatu_mw)

    ev_total_load = micro_load + std_matatu_load + bus_load + rapid_matatu_load
    ev_peak_val = np.max(ev_total_load)
    ev_peak_hour = hours[np.argmax(ev_total_load)]

    # ---------------------------------------------------------
    # PLOT 1: Synthetic 24-Hour Load Profile Stack
    # ---------------------------------------------------------
    plt.figure(figsize=(11, 6.5))
    labels = ['Motorcycles & Tuk-Tuks', 'Standard Matatus (7kW AC Depot)', 'Electric Buses (40kW DC Depot)', 'Rapid Matatus (40kW DC Terminus)']
    colors = ['#1F77B4', '#FF7F0E', '#9467BD', '#D62728']
    
    plt.stackplot(hours, micro_load, std_matatu_load, bus_load, rapid_matatu_load, labels=labels, colors=colors, alpha=0.85)
    plt.plot(hours, ev_total_load, color='black', linewidth=2.5, linestyle='--', label='Aggregate County Peak Load')

    plt.title('Synthetic 24-Hour Load Profile (2030 High-Ambition)', fontsize=14, weight='bold', pad=15)
    plt.ylabel('Coincident Load (MW)', fontsize=12, weight='bold')
    plt.xlabel('Hour of Day', fontsize=12, weight='bold')
    plt.xticks(np.arange(0, 25, 2), [f"{h:02d}:00" for h in np.arange(0, 25, 2)])
    plt.xlim(0, 24)
    plt.ylim(0, ev_peak_val + 1.5)
    plt.grid(True, linestyle='--', alpha=0.5)

    # Off-Peak Tariff Visualization
    plt.axvspan(0, 6, color='green', alpha=0.08)
    plt.axvspan(22, 24, color='green', alpha=0.08)
    plt.text(3, ev_peak_val + 0.5, 'EPRA TOU Off-Peak Window\n(Lowest Tariff)', ha='center', color='darkgreen', fontsize=10, weight='bold')

    plt.annotate(f'Daytime Coincident Peak\n~{ev_peak_val:.1f} MW',
                 xy=(ev_peak_hour, ev_peak_val), xytext=(ev_peak_hour + 2, ev_peak_val + 0.5),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                 fontsize=11, weight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1))

    plt.legend(loc='upper right', bbox_to_anchor=(0.98, 0.95), framealpha=0.9)
    plt.tight_layout()
    plt.savefig(SAVE_PATH_STACK, dpi=300)
    print(f" > Saved Stack Profile to: {SAVE_PATH_STACK}")
    plt.close()

    # ---------------------------------------------------------
    # PLOT 2: Dual-Axis Macro Grid Overlay
    # ---------------------------------------------------------
    # Generate Synthetic National KPLC Baseline
    kplc_load = 1200 + gaussian(hours, 9, 2.0, 600) + gaussian(hours, 14, 4.0, 400) + gaussian(hours, 20, 1.5, 1200)

    fig, ax1 = plt.subplots(figsize=(12, 7.5))

    # Axis 1: National Grid
    ax1.set_xlabel('Hour of Day', fontsize=12, weight='bold')
    ax1.set_ylabel('National Grid Load (MW)', color='black', fontsize=12, weight='bold')
    ax1.fill_between(hours, 0, kplc_load, color='#808080', alpha=0.15)
    line_kplc, = ax1.plot(hours, kplc_load, color='#808080', linewidth=2.5, label='National Grid Load (KPLC)')
    ax1.set_xlim(0, 24)
    ax1.set_ylim(0, 3000)
    ax1.set_xticks(np.arange(0, 25, 2))
    ax1.set_xticklabels([f"{h:02d}:00" for h in np.arange(0, 25, 2)])
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Axis 2: County EV Load
    ax2 = ax1.twinx()
    ax2.set_ylabel("County EV Load (MW)", color='black', fontsize=12, weight='bold')
    ax2.stackplot(hours, micro_load, std_matatu_load, bus_load, rapid_matatu_load, colors=colors, alpha=0.85)
    ax2.set_ylim(0, 8.0)

    proxy_rects = [mpatches.Rectangle((0,0),1,1, facecolor=c, alpha=0.85) for c in colors]
    ax1.legend([line_kplc] + proxy_rects, ['Baseline Current Load Profile (KPLC)'] + labels, loc='upper left', framealpha=0.9, fontsize=9)

    plt.title('County Charging Profile vs. National Daily Load Curve', fontsize=14, weight='bold', pad=15)
    
    kplc_peak = np.max(kplc_load)
    ax1.annotate(f'Current System Peak: ~2,400 MW', xy=(hours[np.argmax(kplc_load)], kplc_peak), 
                 xytext=(hours[np.argmax(kplc_load)] - 5, kplc_peak + 200), 
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8), 
                 fontsize=10, weight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1))

    ax2.annotate(f'County EV Peak\n(Local Distribution Bottleneck)', xy=(ev_peak_hour, ev_peak_val), 
                 xytext=(ev_peak_hour + 1.5, ev_peak_val + 0.5), 
                 arrowprops=dict(facecolor='red', shrink=0.05, width=1.5, headwidth=8), 
                 fontsize=10, weight='bold', color='darkred', bbox=dict(boxstyle="round,pad=0.3", fc="mistyrose", ec="darkred", lw=1))

    plt.tight_layout()
    plt.savefig(SAVE_PATH_DUAL, dpi=300)
    print(f" > Saved Dual-Axis Overlay to: {SAVE_PATH_DUAL}")

if __name__ == "__main__":
    run()
