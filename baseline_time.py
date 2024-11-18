import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 11

wsr_time_dir = 'wsr/time'
baseline_1_time_dir = 'baseline_1/time'
baseline_2_time_dir = 'baseline_2/time'

def load_all_csv(directory):
    data_frames = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            df = pd.read_csv(file_path)
            data_frames.append(df)
    return data_frames

wsr_data_frames = load_all_csv(wsr_time_dir)
baseline_1_data_frames = load_all_csv(baseline_1_time_dir)
baseline_2_data_frames = load_all_csv(baseline_2_time_dir)

def average_termination_time(data_frames):
    termination_times = [df['time_elapsed'].max() for df in data_frames]
    return np.mean(termination_times)

def average_termination_coverage(data_frames):
    termination_coverages = [df['coverage_percent'].iloc[-1] for df in data_frames]
    return np.mean(termination_coverages)

avg_term_time_wsr = average_termination_time(wsr_data_frames)
avg_term_time_baseline_1 = average_termination_time(baseline_1_data_frames)
avg_term_time_baseline_2 = average_termination_time(baseline_2_data_frames)

avg_term_coverage_wsr = min(average_termination_coverage(wsr_data_frames), 90)
avg_term_coverage_baseline_1 = min(average_termination_coverage(baseline_1_data_frames), 90)
avg_term_coverage_baseline_2 = min(average_termination_coverage(baseline_2_data_frames), 90)

# Interpolate coverage percent and calculate std deviation
def interpolate_coverage(data_frames, avg_term_time, avg_term_coverage):
    time_points = np.linspace(0, avg_term_time, 100)
    all_interpolated_coverage = []

    for df in data_frames:
        interpolated_coverage = np.interp(time_points, df['time_elapsed'], df['coverage_percent'])
        all_interpolated_coverage.append(interpolated_coverage)

    avg_interpolated_coverage = np.mean(all_interpolated_coverage, axis=0)
    std_interpolated_coverage = np.std(all_interpolated_coverage, axis=0)
    
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

# Interpolate coverage percent
time_points_wsr, avg_coverage_wsr, std_coverage_wsr = interpolate_coverage(wsr_data_frames, avg_term_time_wsr, avg_term_coverage_wsr)
time_points_baseline_1, avg_coverage_baseline_1, std_coverage_baseline_1 = interpolate_coverage(baseline_1_data_frames, avg_term_time_baseline_1, avg_term_coverage_baseline_1)
time_points_baseline_2, avg_coverage_baseline_2, std_coverage_baseline_2 = interpolate_coverage(baseline_2_data_frames, avg_term_time_baseline_2, avg_term_coverage_baseline_2)

# PLOTTING
plt.figure(figsize=(12, 6))

baseline_1 = '#CD797D'
wsr_line = '#6E954B'
baseline_2 = '#5B838F'
manual_termination = '#7EA28A'

plt.plot(time_points_wsr, avg_coverage_wsr, color=wsr_line, linewidth='2.5', label='WSR')
plt.fill_between(time_points_wsr, avg_coverage_wsr - std_coverage_wsr, avg_coverage_wsr + std_coverage_wsr, color=wsr_line, alpha=0.2)

plt.plot(time_points_baseline_1, avg_coverage_baseline_1, linewidth='2.5', color=baseline_1, label='Baseline 1: Independent')
plt.fill_between(time_points_baseline_1, avg_coverage_baseline_1 - std_coverage_baseline_1, avg_coverage_baseline_1 + std_coverage_baseline_1, color=baseline_1, alpha=0.2)

plt.plot(time_points_baseline_2, avg_coverage_baseline_2, linewidth='2.5', color=baseline_2, label='Baseline 2: Oracle')
plt.fill_between(time_points_baseline_2, avg_coverage_baseline_2 - std_coverage_baseline_2, avg_coverage_baseline_2 + std_coverage_baseline_2, color=baseline_2, alpha=0.2)

plt.scatter([time_points_wsr[-1]], [avg_coverage_wsr[-1]], color='green', s=60, edgecolor='black', zorder=7, label="WSR Termination")
plt.scatter([time_points_baseline_1[-1]], [avg_coverage_baseline_1[-1]], s=60, color='red', edgecolor='black', zorder=7, label="Manual Termination, Baseline 1")
plt.scatter([time_points_baseline_2[-1]], [avg_coverage_baseline_2[-1]], s=60, color='blue', edgecolor='black', zorder=7, label="Manual Termination, Baseline 2")

# Adding vertical lines
plt.vlines(x=time_points_wsr[-1], ymin=0, ymax=avg_coverage_wsr[-1], colors='green', linestyles='dashed')
plt.vlines(x=time_points_baseline_1[-1], ymin=0, ymax=avg_coverage_baseline_1[-1], colors='red', linestyles='dashed')
plt.vlines(x=time_points_baseline_2[-1], ymin=0, ymax=avg_coverage_baseline_2[-1], colors='blue', linestyles='dashed')

plt.xlabel('Time Elapsed (s)')
plt.ylabel('Map Coverage Percent')
plt.title('Map Coverage For Each Baseline, Close')
# plt.legend(loc='lower right')
plt.yticks(np.arange(0, 101, 10)) 
# plt.grid(axis='y')
plt.xticks()
plt.ylim(0, 100) 
plt.show()
