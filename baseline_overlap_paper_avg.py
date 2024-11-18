import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 16

# Define two sets of folders
simulation_folders = {
    'Baseline 1: Independent': 'baseline_1_near_far',
    'Baseline 2: Oracle': 'baseline_2_near_far',
    'WSR': 'wsr_near_far'
}

hardware_folders = {
    'Baseline 1: Independent': 'hw_baseline_consolodated',
    'Baseline 2: Oracle': 'hw_env_1_baseline_2_consolodated',
    'WSR': 'hw_wsr_consolodated'
}

# Used for plotting
colors = {
    'Baseline 1: Independent': '#CD797D',
    'Baseline 2: Oracle': '#5B838F',
    'WSR': '#6E954B'
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
    combined_coverage_df = pd.concat(coverage_data, ignore_index=True)
    return combined_coverage_df

def read_time_data(folder):
    time_data = []
    for file_name in os.listdir(os.path.join(folder, 'time')):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder, 'time', file_name)
            df = pd.read_csv(file_path)
            df['time_elapsed'] = df['time_elapsed'].round()
            df['coverage_percent'] = df['coverage_percent'].round()
            time_data.append(df[['time_elapsed', 'coverage_percent']])
    combined_time_df = pd.concat(time_data, ignore_index=True)
    return combined_time_df

def process_folder(folder):
    coverage_df = read_coverage_data(folder)
    time_df = read_time_data(folder)
    
    merged_df = pd.merge(coverage_df, time_df, left_on='Time Elapsed (s)', right_on='time_elapsed')
    merged_df.drop(columns=['time_elapsed'], inplace=True)
    grouped_df = merged_df.groupby('coverage_percent')['Coverage Overlap (%)'].agg(['mean', 'std']).reset_index()
    
    # Filter to include only coverage_percent between 10 and 90 (manual erorr before and after these points)
    filtered_df = grouped_df[(grouped_df['coverage_percent'] >= 10) & (grouped_df['coverage_percent'] <= 90)]
    
    return filtered_df

def process_folders_set(folders):
    results = {}
    for name, folder in folders.items():
        results[name] = process_folder(folder)
    return results

simulation_results = process_folders_set(simulation_folders)
hardware_results = process_folders_set(hardware_folders)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))


# Simulation Results - Plot
for name, df in simulation_results.items():
    mean_capped = np.minimum(df['mean'], 100)
    std_capped = np.minimum(df['std'], 100 - mean_capped)

    ax1.plot(df['coverage_percent'], mean_capped, label=f'{name}', color=colors[name], linewidth=2)
    ax1.fill_between(df['coverage_percent'], mean_capped - std_capped, mean_capped + std_capped, color=colors[name], alpha=0.2)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.set_xlabel('Total Map Coverage Percent')
ax1.set_ylabel('Average Coverage Overlap (%)')
ax1.set_title('Simulation')
ax1.legend()

# Hardware Results - Plot
for name, df in hardware_results.items():
    mean_capped = np.minimum(df['mean'], 100)
    std_capped = np.minimum(df['std'], 100 - mean_capped)

    ax2.plot(df['coverage_percent'], mean_capped, label=f'{name}', color=colors[name], linewidth=2)
    ax2.fill_between(df['coverage_percent'], mean_capped - std_capped, mean_capped + std_capped, color=colors[name], alpha=0.2)

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_xlabel('Total Map Coverage Percent')
ax2.set_ylabel('Average Coverage Overlap (%)')
ax2.set_title('Hardware')

plt.suptitle('Robot Map Coverage Overlap')
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

plt.show()
