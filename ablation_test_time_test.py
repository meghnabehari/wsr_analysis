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
    'WSR': 'ablation_wsr'
}

colors = {
    'Ablation - No Beta': '#CD797D',
    'Ablation - No View Points': '#5B838F',
    'Ablation - Neither Beta nor View Points': '#6E954B',
    'WSR': '#884E6D'
}

# Load data function with sorting and limiting to first 5 files for all folders
def load_all_csv(directory, limit_first_five=False):
    data_frames = []
    files = os.listdir(directory)
    
    # Sort files by the final number in the filename
    files = sorted(files, key=lambda x: int(re.search(r'(\d+)(?=\D*$)', x).group()))

    # If limiting to the first 5 files, slice the list
    if limit_first_five:
        files = files[4:]
    
    # Load CSV files
    for filename in files:
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            data_frames.append(df)
    return data_frames

# Average termination time and coverage calculations
def average_termination_time(data_frames):
    termination_times = [df['time_elapsed'].max() for df in data_frames]
    return np.mean(termination_times), termination_times

def average_termination_coverage(data_frames):
    termination_coverages = [df['coverage_percent'].iloc[-1] for df in data_frames]
    return np.mean(termination_coverages)

# Interpolation function
def interpolate_coverage(data_frames, avg_term_time, avg_term_coverage):
    time_points = np.linspace(0, avg_term_time, 100)
    all_interpolated_coverage = []

    for df in data_frames:
        interpolated_coverage = np.interp(time_points, df['time_elapsed'], df['coverage_percent'])
        all_interpolated_coverage.append(interpolated_coverage)

    avg_interpolated_coverage = np.mean(all_interpolated_coverage, axis=0)
    std_interpolated_coverage = np.std(all_interpolated_coverage, axis=0)

    # Cap coverage to max term coverage or 90
    for i in range(len(avg_interpolated_coverage)):
        if avg_interpolated_coverage[i] >= avg_term_coverage:
            avg_interpolated_coverage = avg_interpolated_coverage[:i+1]
            std_interpolated_coverage = std_interpolated_coverage[:i+1]
            time_points = time_points[:i+1]
            avg_interpolated_coverage[-1] = avg_term_coverage
            std_interpolated_coverage[-1] = 0
            break
    
    return time_points, avg_interpolated_coverage, std_interpolated_coverage

# Process all folders with limiting for all folders
results = {}
for name, folder in folders.items():
    # Set limit_first_five to True for all folders
    limit_first_five = True
    data_frames = load_all_csv(os.path.join(folder, 'time'), limit_first_five)
    avg_term_time, _ = average_termination_time(data_frames)
    avg_term_coverage = min(average_termination_coverage(data_frames), 90)
    time_points, avg_coverage, std_coverage = interpolate_coverage(data_frames, avg_term_time, avg_term_coverage)
    results[name] = (time_points, avg_coverage, std_coverage)

# Plotting all results on a single plot
fig, ax = plt.subplots(figsize=(10, 7))

for name, (time_points, avg_coverage, std_coverage) in results.items():
    ax.plot(time_points, avg_coverage, label=name, color=colors[name], linewidth=3.5)
    ax.fill_between(time_points, avg_coverage - std_coverage, avg_coverage + std_coverage, color=colors[name], alpha=0.2)

# Customize the plot
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_xlabel('Time Elapsed (s)')
ax.set_ylabel('Map Coverage Percent')
ax.set_title('Time vs Map Coverage Percent')
ax.set_ylim(0, 100)
ax.legend(fontsize='x-small', loc='upper left', framealpha=0.5)

plt.tight_layout()
plt.show()
