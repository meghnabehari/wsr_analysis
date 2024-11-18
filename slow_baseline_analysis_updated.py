import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 16

main_folder_slow_baseline = "slow_baseline"
main_folder_far_wsr_slow = "far_wsr_slow_updated"
sub_folders = ["bottom", "upper_left", "upper_right"]

region_coverage = {}

for sub_folder in sub_folders:
    time_folder_path = os.path.join(main_folder_slow_baseline, sub_folder, "time")
    files = os.listdir(time_folder_path)
    
    first_file_path = os.path.join(time_folder_path, files[0])
    df = pd.read_csv(first_file_path)
    
    df['time_elapsed'] = df['time_elapsed'].round()
    
    df_grouped = df.groupby('time_elapsed')['coverage_percent'].max().reset_index()
    df_grouped['coverage_percent'] = df_grouped['coverage_percent'] / 3
    
    region_coverage[sub_folder] = df_grouped.set_index('time_elapsed')

max_time_slow_baseline = int(max(df.index.max() for df in region_coverage.values()))
actual_max_time = int(max(df.index.max() for df in region_coverage.values()))

for region, df in region_coverage.items():
    region_coverage[region] = df.reindex(range(0, actual_max_time + 1)).ffill()

total_coverage = sum(region_coverage.values())
total_coverage = total_coverage.reset_index()

total_coverage = total_coverage[total_coverage['coverage_percent'] <= 95]

time_folder_path_wsr = os.path.join(main_folder_far_wsr_slow, "time")
files_wsr = os.listdir(time_folder_path_wsr)

termination_coverage_percent = []

for file in files_wsr:
    file_path_wsr = os.path.join(time_folder_path_wsr, file)
    df_wsr = pd.read_csv(file_path_wsr)
    df_wsr['time_elapsed'] = df_wsr['time_elapsed'].round()
    df_grouped_wsr = df_wsr.groupby('time_elapsed')['coverage_percent'].max().reset_index()
    
    df_grouped_wsr = df_grouped_wsr[df_grouped_wsr['coverage_percent'] <= 95]
    
    last_coverage_percent = df_grouped_wsr['coverage_percent'].iloc[-1]
    termination_coverage_percent.append(last_coverage_percent)

average_termination_coverage_percent = np.mean(termination_coverage_percent)

print(f"Average Termination Coverage Percent across all WSR files: {average_termination_coverage_percent:.2f}%")

plt.figure(figsize=(10, 6))
plt.plot(total_coverage['time_elapsed'], total_coverage['coverage_percent'], marker='o', label='Slow Baseline Total Coverage')
plt.plot(df_grouped_wsr['time_elapsed'], df_grouped_wsr['coverage_percent'], marker='x', label='Far WSR Slow Coverage', color='orange')

plt.xlabel('Time Elapsed (s)')
plt.ylabel('Coverage Percent')
plt.title('Coverage Percent vs. Time Elapsed')
plt.legend()
plt.grid(True)
plt.ylim(0, 98)
plt.show()
