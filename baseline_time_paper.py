import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 11

# Define directories for each data set
wsr_time_dir_set_1 = 'wsr/time'
baseline_1_time_dir_set_1 = 'baseline_1/time'
baseline_2_time_dir_set_1 = 'baseline_2/time'

wsr_time_dir_set_2 = 'hw_wsr_consolodated/time'
baseline_1_time_dir_set_2 = 'hw_baseline_consolodated/time'
baseline_2_time_dir_set_2 = 'hw_env_1_baseline_2_consolodated/time'
def load_all_csv(directory):
    data_frames = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            data_frames.append(df)
    return data_frames

# Load data for both sets
wsr_data_frames_set_1 = load_all_csv(wsr_time_dir_set_1)
baseline_1_data_frames_set_1 = load_all_csv(baseline_1_time_dir_set_1)
baseline_2_data_frames_set_1 = load_all_csv(baseline_2_time_dir_set_1)

wsr_data_frames_set_2 = load_all_csv(wsr_time_dir_set_2)
baseline_1_data_frames_set_2 = load_all_csv(baseline_1_time_dir_set_2)
baseline_2_data_frames_set_2 = load_all_csv(baseline_2_time_dir_set_2)

def average_termination_time(data_frames):
    termination_times = [df['time_elapsed'].max() for df in data_frames]
    return np.mean(termination_times)

def average_termination_coverage(data_frames):
    termination_coverages = [df['coverage_percent'].iloc[-1] for df in data_frames]
    return np.mean(termination_coverages)

# Calculate average termination time and coverage for both sets
avg_term_time_wsr_set_1 = average_termination_time(wsr_data_frames_set_1)
avg_term_time_baseline_1_set_1 = average_termination_time(baseline_1_data_frames_set_1)
avg_term_time_baseline_2_set_1 = average_termination_time(baseline_2_data_frames_set_1)

avg_term_coverage_wsr_set_1 = min(average_termination_coverage(wsr_data_frames_set_1), 90)
avg_term_coverage_baseline_1_set_1 = min(average_termination_coverage(baseline_1_data_frames_set_1), 90)
avg_term_coverage_baseline_2_set_1 = min(average_termination_coverage(baseline_2_data_frames_set_1), 90)

avg_term_time_wsr_set_2 = average_termination_time(wsr_data_frames_set_2)
avg_term_time_baseline_1_set_2 = average_termination_time(baseline_1_data_frames_set_2)
avg_term_time_baseline_2_set_2 = average_termination_time(baseline_2_data_frames_set_2)

avg_term_coverage_wsr_set_2 = min(average_termination_coverage(wsr_data_frames_set_2), 90)
avg_term_coverage_baseline_1_set_2 = min(average_termination_coverage(baseline_1_data_frames_set_2), 90)
avg_term_coverage_baseline_2_set_2 = min(average_termination_coverage(baseline_2_data_frames_set_2), 90)

# Interpolate coverage percent and calculate std deviation
def interpolate_coverage(data_frames, avg_term_time, avg_term_coverage):
    time_points = np.linspace(0, avg_term_time, 100)
    all_interpolated_coverage = []

    for df in data_frames:
        interpolated_coverage = np.interp(time_points, df['time_elapsed'], df['coverage_percent'])
        all_interpolated_coverage.append(interpolated_coverage)

    avg_interpolated_coverage = np.mean(all_interpolated_coverage, axis=0)
    std_interpolated_coverage = np.std(all_interpolated_coverage, axis=0)  # Fixed typo

    # Find the point where the average coverage reaches 90 or the average termination coverage, whichever is first
    for i in range(len(avg_interpolated_coverage)):
        if avg_interpolated_coverage[i] >= avg_term_coverage:
            avg_interpolated_coverage = avg_interpolated_coverage[:i+1]
            std_interpolated_coverage = std_interpolated_coverage[:i+1]
            time_points = time_points[:i+1]
            avg_interpolated_coverage[-1] = avg_term_coverage
            std_interpolated_coverage[-1] = 0
            break
    
    return time_points, avg_interpolated_coverage, std_interpolated_coverage

# Interpolate coverage percent for both sets
time_points_wsr_set_1, avg_coverage_wsr_set_1, std_coverage_wsr_set_1 = interpolate_coverage(wsr_data_frames_set_1, avg_term_time_wsr_set_1, avg_term_coverage_wsr_set_1)
time_points_baseline_1_set_1, avg_coverage_baseline_1_set_1, std_coverage_baseline_1_set_1 = interpolate_coverage(baseline_1_data_frames_set_1, avg_term_time_baseline_1_set_1, avg_term_coverage_baseline_1_set_1)
time_points_baseline_2_set_1, avg_coverage_baseline_2_set_1, std_coverage_baseline_2_set_1 = interpolate_coverage(baseline_2_data_frames_set_1, avg_term_time_baseline_2_set_1, avg_term_coverage_baseline_2_set_1)

time_points_wsr_set_2, avg_coverage_wsr_set_2, std_coverage_wsr_set_2 = interpolate_coverage(wsr_data_frames_set_2, avg_term_time_wsr_set_2, avg_term_coverage_wsr_set_2)
time_points_baseline_1_set_2, avg_coverage_baseline_1_set_2, std_coverage_baseline_1_set_2 = interpolate_coverage(baseline_1_data_frames_set_2, avg_term_time_baseline_1_set_2, avg_term_coverage_baseline_1_set_2)
time_points_baseline_2_set_2, avg_coverage_baseline_2_set_2, std_coverage_baseline_2_set_2 = interpolate_coverage(baseline_2_data_frames_set_2, avg_term_time_baseline_2_set_2, avg_term_coverage_baseline_2_set_2)

# PLOTTING
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

baseline_1 = '#CD797D'
wsr_line = '#6E954B'
baseline_2 = '#5B838F'

# Plot for Set 1
ax1.plot(time_points_wsr_set_1, avg_coverage_wsr_set_1, color=wsr_line, linewidth=2.5, label='WSR')
ax1.fill_between(time_points_wsr_set_1, avg_coverage_wsr_set_1 - std_coverage_wsr_set_1, avg_coverage_wsr_set_1 + std_coverage_wsr_set_1, color=wsr_line, alpha=0.2)

ax1.plot(time_points_baseline_1_set_1, avg_coverage_baseline_1_set_1, linewidth=2.5, color=baseline_1, label='Baseline 1: Independent')
ax1.fill_between(time_points_baseline_1_set_1, avg_coverage_baseline_1_set_1 - std_coverage_baseline_1_set_1, avg_coverage_baseline_1_set_1 + std_coverage_baseline_1_set_1, color=baseline_1, alpha=0.2)

ax1.plot(time_points_baseline_2_set_1, avg_coverage_baseline_2_set_1, linewidth=2.5, color=baseline_2, label='Baseline 2: Oracle')
ax1.fill_between(time_points_baseline_2_set_1, avg_coverage_baseline_2_set_1 - std_coverage_baseline_2_set_1, avg_coverage_baseline_2_set_1 + std_coverage_baseline_2_set_1, color=baseline_2, alpha=0.2)

ax1.scatter([time_points_wsr_set_1[-1]], [avg_coverage_wsr_set_1[-1]], color='green', s=60, edgecolor='black', zorder=7)
ax1.scatter([time_points_baseline_1_set_1[-1]], [avg_coverage_baseline_1_set_1[-1]], s=60, color='red', edgecolor='black', zorder=7)
ax1.scatter([time_points_baseline_2_set_1[-1]], [avg_coverage_baseline_2_set_1[-1]], s=60, color='blue', edgecolor='black', zorder=7)

# Adding vertical lines for Set 1
ax1.vlines(x=time_points_wsr_set_1[-1], ymin=0, ymax=avg_coverage_wsr_set_1[-1], colors='green', linestyles='dashed')
ax1.vlines(x=time_points_baseline_1_set_1[-1], ymin=0, ymax=avg_coverage_baseline_1_set_1[-1], colors='red', linestyles='dashed')
ax1.vlines(x=time_points_baseline_2_set_1[-1], ymin=0, ymax=avg_coverage_baseline_2_set_1[-1], colors='blue', linestyles='dashed')

ax1.set_xlabel('Time Elapsed (s)')
ax1.set_ylabel('Map Coverage Percent')
ax1.set_title('Simulation')
ax1.set_ylim(0, 100)
ax1.set_yticks(np.arange(0, 101, 10))  # Correct method for setting yticks
ax1.legend(loc='upper left')

# Plot for Set 2
ax2.plot(time_points_wsr_set_2, avg_coverage_wsr_set_2, color=wsr_line, linewidth=2.5, label='WSR Set 2')
ax2.fill_between(time_points_wsr_set_2, avg_coverage_wsr_set_2 - std_coverage_wsr_set_2, avg_coverage_wsr_set_2 + std_coverage_wsr_set_2, color=wsr_line, alpha=0.2)

ax2.plot(time_points_baseline_1_set_2, avg_coverage_baseline_1_set_2, linewidth=2.5, color=baseline_1, label='Baseline 1: Independent Set 2')
ax2.fill_between(time_points_baseline_1_set_2, avg_coverage_baseline_1_set_2 - std_coverage_baseline_1_set_2, avg_coverage_baseline_1_set_2 + std_coverage_baseline_1_set_2, color=baseline_1, alpha=0.2)

ax2.plot(time_points_baseline_2_set_2, avg_coverage_baseline_2_set_2, linewidth=2.5, color=baseline_2, label='Baseline 2: Oracle Set 2')
ax2.fill_between(time_points_baseline_2_set_2, avg_coverage_baseline_2_set_2 - std_coverage_baseline_2_set_2, avg_coverage_baseline_2_set_2 + std_coverage_baseline_2_set_2, color=baseline_2, alpha=0.2)

ax2.scatter([time_points_wsr_set_2[-1]], [avg_coverage_wsr_set_2[-1]], color='green', s=60, edgecolor='black', zorder=7)
ax2.scatter([time_points_baseline_1_set_2[-1]], [avg_coverage_baseline_1_set_2[-1]], s=60, color='red', edgecolor='black')
ax2.scatter([time_points_baseline_2_set_2[-1]], [avg_coverage_baseline_2_set_2[-1]], s=60, color='blue', edgecolor='black')

# Adding vertical lines for Set 2
ax2.vlines(x=time_points_wsr_set_2[-1], ymin=0, ymax=avg_coverage_wsr_set_2[-1], colors='green', linestyles='dashed')
ax2.vlines(x=time_points_baseline_1_set_2[-1], ymin=0, ymax=avg_coverage_baseline_1_set_2[-1], colors='red', linestyles='dashed')
ax2.vlines(x=time_points_baseline_2_set_2[-1], ymin=0, ymax=avg_coverage_baseline_2_set_2[-1], colors='blue', linestyles='dashed')

ax2.set_xlabel('Time Elapsed (s)')
ax2.set_ylabel('Map Coverage Percent')
ax2.set_title('Hardware')
ax2.set_ylim(0, 100)
ax2.set_yticks(np.arange(0, 101, 10))  # Correct method for setting yticks
# ax2.legend(loc='lower right')

# Remove top and right spines for both plots
for ax in [ax1, ax2]:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.suptitle('Exploration Map Coverage and Termination Time')

# Adjust layout to prevent overlap
plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

plt.show()