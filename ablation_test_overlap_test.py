import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 17

# Define all folders and corresponding colors
folders = {
    'Ablation - No Beta': 'ablation_beta',
    'Ablation - No View Points': 'ablation_view_points',
    'Ablation - Neither Beta nor View Points': 'ablation_all',
    'WSR': 'ablation_wsr',
}

colors = {
    'Ablation - No Beta': '#CD797D',
    'Ablation - No View Points': '#5B838F',
    'Ablation - Neither Beta nor View Points': '#6E954B',
    'WSR': '#884E6D',
}

# Read coverage data with sorting and limiting for all folders
def read_coverage_data(folder, limit_first_five=True):
    coverage_data = []
    files = os.listdir(os.path.join(folder, 'coverage'))

    # Sort files by the final number in the filename
    files = sorted(files, key=lambda x: int(re.search(r'(\d+)(?=\D*$)', x).group()))

    # If limiting to the first 5 files, slice the list
    if limit_first_five:
        files = files[5:]

    for file_name in files:
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder, 'coverage', file_name)
            df = pd.read_csv(file_path)
            df['Time Elapsed (s)'] = df['Time Elapsed (s)'].round()
            df['Coverage Overlap (%)'] = df['Coverage Overlap (%)'].apply(lambda x: 5 if x <= 0 else x)
            coverage_data.append(df[['Time Elapsed (s)', 'Coverage Overlap (%)']])
    return coverage_data

# Read time data with sorting and limiting for all folders
def read_time_data(folder, limit_first_five=True):
    time_data = []
    files = os.listdir(os.path.join(folder, 'time'))

    # Sort files by the final number in the filename
    files = sorted(files, key=lambda x: int(re.search(r'(\d+)(?=\D*$)', x).group()))

    # If limiting to the first 5 files, slice the list
    if limit_first_five:
        files = files[5:]

    for file_name in files:
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

def process_folder(folder, limit_first_five=True):
    coverage_data = read_coverage_data(folder, limit_first_five)
    time_data = read_time_data(folder, limit_first_five)
    
    avg_coverage, avg_overlap, std_overlap = interpolate_data(coverage_data, time_data)
    
    return avg_coverage, avg_overlap, std_overlap

# Process all folders with limiting for all folders
all_results = {}
for name, folder in folders.items():
    avg_coverage, avg_overlap, std_overlap = process_folder(folder, limit_first_five=True)
    all_results[name] = (avg_coverage, avg_overlap, std_overlap)

# Plotting all results on a single plot
fig, ax = plt.subplots(figsize=(10, 7))

for name, (avg_coverage, avg_overlap, std_overlap) in all_results.items():
    ax.plot(avg_coverage, avg_overlap, label=name, color=colors[name], linewidth=3.5)
    ax.fill_between(avg_coverage, avg_overlap - std_overlap, avg_overlap + std_overlap, color=colors[name], alpha=0.2)

# Customize the plot
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel('Total Map Coverage Percent')
ax.set_ylabel('Average Coverage Overlap (%)')
ax.set_title('Robot Map Coverage Overlap')
ax.legend(fontsize='x-small', loc='upper left', framealpha=0.5)

plt.tight_layout()
plt.show()
