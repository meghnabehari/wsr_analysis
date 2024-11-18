import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 16

# Define directories for each data set
wsr_time_dir_set_1 = 'wsr_near_far/time'
baseline_1_time_dir_set_1 = 'baseline_1_near_far/time'
baseline_2_time_dir_set_1 = 'baseline_2_near_far/time'

wsr_time_dir_set_2 = 'hw_wsr_consolodated/time'
baseline_1_time_dir_set_2 = 'hw_baseline_consolodated/time'
baseline_2_time_dir_set_2 = 'hw_env_1_baseline_2_consolodated/time'

def load_and_process_time_data(directory):
    time_data = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            df['time_elapsed'] = df['time_elapsed'].round()
            df['coverage_percent'] = df['coverage_percent'].round()
            time_data.append(df[['time_elapsed', 'coverage_percent']])
    
    combined_time_df = pd.concat(time_data, ignore_index=True)
    grouped_df = combined_time_df.groupby('time_elapsed')['coverage_percent'].agg(['mean', 'std']).reset_index()
    
    # Filter to include only coverage_percent between 10 and 90
    filtered_df = grouped_df[(grouped_df['mean'] >= 10) & (grouped_df['mean'] <= 90)]
    
    return filtered_df

# Load and process data for both sets
wsr_data_set_1 = load_and_process_time_data(wsr_time_dir_set_1)
baseline_1_data_set_1 = load_and_process_time_data(baseline_1_time_dir_set_1)
baseline_2_data_set_1 = load_and_process_time_data(baseline_2_time_dir_set_1)

wsr_data_set_2 = load_and_process_time_data(wsr_time_dir_set_2)
baseline_1_data_set_2 = load_and_process_time_data(baseline_1_time_dir_set_2)
baseline_2_data_set_2 = load_and_process_time_data(baseline_2_time_dir_set_2)

# PLOTTING
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

colors = {
    'Baseline 1': '#CD797D',
    'Baseline 2': '#5B838F',
    'WSR': '#6E954B'
}

# Plot for Set 1
ax1.plot(wsr_data_set_1['time_elapsed'], wsr_data_set_1['mean'], color=colors['WSR'], linewidth=2.5, label='WSR')
ax1.fill_between(wsr_data_set_1['time_elapsed'], wsr_data_set_1['mean'] - wsr_data_set_1['std'], wsr_data_set_1['mean'] + wsr_data_set_1['std'], color=colors['WSR'], alpha=0.2)

ax1.plot(baseline_1_data_set_1['time_elapsed'], baseline_1_data_set_1['mean'], color=colors['Baseline 1'], linewidth=2.5, label='Baseline 1: Independent')
ax1.fill_between(baseline_1_data_set_1['time_elapsed'], baseline_1_data_set_1['mean'] - baseline_1_data_set_1['std'], baseline_1_data_set_1['mean'] + baseline_1_data_set_1['std'], color=colors['Baseline 1'], alpha=0.2)

ax1.plot(baseline_2_data_set_1['time_elapsed'], baseline_2_data_set_1['mean'], color=colors['Baseline 2'], linewidth=2.5, label='Baseline 2: Oracle')
ax1.fill_between(baseline_2_data_set_1['time_elapsed'], baseline_2_data_set_1['mean'] - baseline_2_data_set_1['std'], baseline_2_data_set_1['mean'] + baseline_2_data_set_1['std'], color=colors['Baseline 2'], alpha=0.2)

ax1.set_xlabel('Time Elapsed (s)')
ax1.set_ylabel('Map Coverage Percent')
ax1.set_title('Simulation')
ax1.set_ylim(0, 100)
ax1.set_yticks(np.arange(0, 101, 10))  
legend = ax1.legend(fontsize='small', loc='upper left')
legend.get_frame().set_alpha(0.5)

# Plot for Set 2
ax2.plot(wsr_data_set_2['time_elapsed'], wsr_data_set_2['mean'], color=colors['WSR'], linewidth=2.5, label='WSR Set 2')
ax2.fill_between(wsr_data_set_2['time_elapsed'], wsr_data_set_2['mean'] - wsr_data_set_2['std'], wsr_data_set_2['mean'] + wsr_data_set_2['std'], color=colors['WSR'], alpha=0.2)

ax2.plot(baseline_1_data_set_2['time_elapsed'], baseline_1_data_set_2['mean'], color=colors['Baseline 1'], linewidth=2.5, label='Baseline 1: Independent Set 2')
ax2.fill_between(baseline_1_data_set_2['time_elapsed'], baseline_1_data_set_2['mean'] - baseline_1_data_set_2['std'], baseline_1_data_set_2['mean'] + baseline_1_data_set_2['std'], color=colors['Baseline 1'], alpha=0.2)

ax2.plot(baseline_2_data_set_2['time_elapsed'], baseline_2_data_set_2['mean'], color=colors['Baseline 2'], linewidth=2.5, label='Baseline 2: Oracle Set 2')
ax2.fill_between(baseline_2_data_set_2['time_elapsed'], baseline_2_data_set_2['mean'] - baseline_2_data_set_2['std'], baseline_2_data_set_2['std'] + baseline_2_data_set_2['mean'], color=colors['Baseline 2'], alpha=0.2)

ax2.set_xlabel('Time Elapsed (s)')
ax2.set_ylabel('Map Coverage Percent')
ax2.set_title('Hardware')
ax2.set_ylim(0, 100)
ax2.set_yticks(np.arange(0, 101, 10))  

# Remove top and right spines for both plots
for ax in [ax1, ax2]:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.suptitle('Exploration Map Coverage and Termination Time')

# Adjust layout to prevent overlap
plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

plt.show()
