import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 17

# Define two sets of folders
simulation_folders = {
    'Baseline-1: Independent Exploration': 'baseline_1_near_far',
    'WiSER-X': 'wsr_near_far',
    'Baseline-2: Full Information Exchange': 'baseline_2_near_far'
}

hardware_folders = {
    'Baseline-1: Independent Exploration': 'hw_baseline_consolodated',
    'WiSER-X': 'hw_wsr_consolodated',
    'Baseline-2: Full Information Exchange': 'hw_env_1_baseline_2_consolodated',
}

# Used for plotting
colors = {
    'Baseline-1: Independent Exploration': '#CD797D',
    'Baseline-2: Full Information Exchange': '#5B838F',
    'WiSER-X': '#6E954B'
}

def read_coverage_data(folder):
    coverage_data = []
    for file_name in os.listdir(os.path.join(folder, 'coverage')):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder, 'coverage', file_name)
            df = pd.read_csv(file_path)
            df['Time Elapsed (s)'] = df['Time Elapsed (s)'].round()
            df['Coverage Overlap (%)'] = df['Coverage Overlap (%)'].apply(lambda x: 5 if x <= 0 else x)
            coverage_data.append(df[['Time Elapsed (s)', 'Coverage Overlap (%)']])
    return coverage_data

def read_time_data(folder):
    time_data = []
    for file_name in os.listdir(os.path.join(folder, 'time')):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder, 'time', file_name)
            df = pd.read_csv(file_path)
            df['time_elapsed'] = df['time_elapsed'].round()
            df['coverage_percent'] = df['coverage_percent'].round()
            time_data.append(df[['time_elapsed', 'coverage_percent']])
    return time_data

def interpolate_data(coverage_data, time_data):
    time_points = np.linspace(0, max(df['time_elapsed'].max() for df in time_data), 100)
    all_interpolated_coverage = []
    all_interpolated_overlap = []
    
    for coverage_df, time_df in zip(coverage_data, time_data):
        interpolated_coverage = np.interp(time_points, time_df['time_elapsed'], time_df['coverage_percent'])
        interpolated_overlap = np.interp(time_points, coverage_df['Time Elapsed (s)'], coverage_df['Coverage Overlap (%)'])
        
        all_interpolated_coverage.append(interpolated_coverage)
        all_interpolated_overlap.append(interpolated_overlap)
    
    avg_interpolated_coverage = np.mean(all_interpolated_coverage, axis=0)
    avg_interpolated_overlap = np.mean(all_interpolated_overlap, axis=0)
    std_interpolated_overlap = np.std(all_interpolated_overlap, axis=0)
    
    # Capping the values
    avg_interpolated_overlap = np.minimum(avg_interpolated_overlap, 100)
    std_interpolated_overlap = np.minimum(std_interpolated_overlap, 100 - avg_interpolated_overlap)
    
    return avg_interpolated_coverage, avg_interpolated_overlap, std_interpolated_overlap

def process_folder(folder):
    coverage_data = read_coverage_data(folder)
    time_data = read_time_data(folder)
    
    avg_coverage, avg_overlap, std_overlap = interpolate_data(coverage_data, time_data)
    
    return avg_coverage, avg_overlap, std_overlap

def process_folders_set(folders):
    results = {}
    for name, folder in folders.items():
        avg_coverage, avg_overlap, std_overlap = process_folder(folder)
        results[name] = (avg_coverage, avg_overlap, std_overlap)
    return results

simulation_results = process_folders_set(simulation_folders)
hardware_results = process_folders_set(hardware_folders)

# Calculate and print raw differences at termination for Simulation
wsr_simulation_overlap = simulation_results['WiSER-X'][1][-1]
baseline_1_simulation_overlap = simulation_results['Baseline-1: Independent Exploration'][1][-1]
baseline_2_simulation_overlap = simulation_results['Baseline-2: Full Information Exchange'][1][-1]

raw_diff_simulation_baseline_1 = wsr_simulation_overlap - baseline_1_simulation_overlap
raw_diff_simulation_baseline_2 = wsr_simulation_overlap - baseline_2_simulation_overlap

print(f"Raw Difference in Termination Coverage Overlap (Simulation) - WSR vs Baseline 1: {raw_diff_simulation_baseline_1:.2f}%")
print(f"Raw Difference in Termination Coverage Overlap (Simulation) - WSR vs Baseline 2: {raw_diff_simulation_baseline_2:.2f}%")

# Calculate and print raw differences at termination for Hardware
wsr_hardware_overlap = hardware_results['WiSER-X'][1][-1]
baseline_1_hardware_overlap = hardware_results['Baseline-1: Independent Exploration'][1][-1]
baseline_2_hardware_overlap = hardware_results['Baseline-2: Full Information Exchange'][1][-1]

raw_diff_hardware_baseline_1 = wsr_hardware_overlap - baseline_1_hardware_overlap
raw_diff_hardware_baseline_2 = wsr_hardware_overlap - baseline_2_hardware_overlap

print(f"Raw Difference in Termination Coverage Overlap (Hardware) - WSR vs Baseline 1: {raw_diff_hardware_baseline_1:.2f}%")
print(f"Raw Difference in Termination Coverage Overlap (Hardware) - WSR vs Baseline 2: {raw_diff_hardware_baseline_2:.2f}%")

# Plotting
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Simulation Results - Plot
for name, (avg_coverage, avg_overlap, std_overlap) in simulation_results.items():
    ax1.plot(avg_coverage, avg_overlap, label=f'{name}', color=colors[name], linewidth=3.5)
    ax1.fill_between(avg_coverage, avg_overlap - std_overlap, avg_overlap + std_overlap, color=colors[name], alpha=0.2)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.set_xlabel('Total Map Coverage Percent')
ax1.set_ylabel('Average Coverage Overlap (%)')
ax1.set_title('Simulation')
# ax1.set_xlim(5, 100)
legend = ax1.legend(fontsize='x-small', loc='upper left')
legend.get_frame().set_alpha(0.5)

# Hardware Results - Plot
for name, (avg_coverage, avg_overlap, std_overlap) in hardware_results.items():
    ax2.plot(avg_coverage, avg_overlap, label=f'{name}', color=colors[name], linewidth=3.5)
    ax2.fill_between(avg_coverage, avg_overlap - std_overlap, avg_overlap + std_overlap, color=colors[name], alpha=0.2)

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_xlabel('Total Map Coverage Percent')
ax2.set_ylabel('Average Coverage Overlap (%)')
ax2.set_title('Hardware')
ax2.set_xlim(5, 100)
legend2 = ax2.legend(fontsize='x-small', loc='upper left')
legend2.get_frame().set_alpha(0.5)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
