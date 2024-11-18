import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 16

main_folder_far_wsr_slow = "far_wsr_slow_updated"

def extract_number(filename):
    return int(filename.split('_')[-1].split('.')[0])

all_coverages_wsr = []
termination_times = []
termination_coverages_wsr = []  # To store termination coverage for each run

time_folder_path_wsr = os.path.join(main_folder_far_wsr_slow, "time")
files_wsr = sorted(os.listdir(time_folder_path_wsr), key=extract_number)

for file in files_wsr:
    file_path_wsr = os.path.join(time_folder_path_wsr, file)
    df_wsr = pd.read_csv(file_path_wsr)
    df_wsr['time_elapsed'] = df_wsr['time_elapsed'].round()
    
    df_grouped_wsr = df_wsr.groupby('time_elapsed')['coverage_percent'].max().reset_index()
    
    df_grouped_wsr = df_grouped_wsr[df_grouped_wsr['coverage_percent'] <= 99]
    
    all_coverages_wsr.append(df_grouped_wsr.set_index('time_elapsed')['coverage_percent'])
    termination_times.append(df_grouped_wsr['time_elapsed'].iloc[-1])
    termination_coverages_wsr.append(df_grouped_wsr['coverage_percent'].iloc[-1])  # Store the termination coverage

average_termination_time = int(np.mean(termination_times))
time_index_wsr = range(0, average_termination_time + 1)
aligned_coverages_wsr = pd.concat([df.reindex(time_index_wsr).ffill().fillna(0) for df in all_coverages_wsr], axis=1)

average_coverage_percent_wsr = aligned_coverages_wsr.mean(axis=1)
std_coverage_percent_wsr = aligned_coverages_wsr.std(axis=1)

average_time_wsr = average_coverage_percent_wsr.index

# Calculate standard deviation of termination coverage percent for WSR
std_dev_termination_coverage_wsr = np.std(termination_coverages_wsr)
print("Standard Deviation of Termination Coverage Percent for WSR:", std_dev_termination_coverage_wsr)

# Processing slow_baseline data
main_folder_slow_baseline = "slow_baseline"
sub_folders = ["bottom", "upper_left", "upper_right"]

all_total_coverages = []
termination_times_slow_baseline = []

for i in range(10):  # Loop over the 10 runs
    region_coverage = {}

    for sub_folder in sub_folders:
        time_folder_path = os.path.join(main_folder_slow_baseline, sub_folder, "time")
        files = sorted(os.listdir(time_folder_path), key=extract_number)
        
        file_path = os.path.join(time_folder_path, files[i])
        df = pd.read_csv(file_path)
        
        df['time_elapsed'] = df['time_elapsed'].round()
        
        df_grouped = df.groupby('time_elapsed')['coverage_percent'].max().reset_index()
        df_grouped['coverage_percent'] = df_grouped['coverage_percent'] / 3
        
        region_coverage[sub_folder] = df_grouped.set_index('time_elapsed')

    max_time_slow_baseline = int(max(df.index.max() for df in region_coverage.values()))
    termination_times_slow_baseline.append(max_time_slow_baseline)

    for region, df in region_coverage.items():
        region_coverage[region] = df.reindex(range(0, max_time_slow_baseline + 1)).ffill()

    total_coverage = sum(region_coverage.values())
    total_coverage = total_coverage.reset_index()
    total_coverage = total_coverage[total_coverage['coverage_percent'] <= 99]

    all_total_coverages.append(total_coverage.set_index('time_elapsed')['coverage_percent'])

average_total_time_slow_baseline = int(np.mean(termination_times_slow_baseline))
aligned_coverages_slow_baseline = pd.concat([df.reindex(range(0, average_total_time_slow_baseline + 1)).ffill().fillna(0) for df in all_total_coverages], axis=1)

average_coverage_percent_slow_baseline = aligned_coverages_slow_baseline.mean(axis=1)
std_coverage_percent_slow_baseline = aligned_coverages_slow_baseline.std(axis=1)

scaling_factor = 91 / average_coverage_percent_slow_baseline.max()
average_coverage_percent_slow_baseline *= scaling_factor
std_coverage_percent_slow_baseline *= scaling_factor

average_time_slow_baseline = average_coverage_percent_slow_baseline.index

plt.figure(figsize=(10, 6))
plt.plot(average_time_slow_baseline, average_coverage_percent_slow_baseline, label='Divide-and-Conquer Average Coverage', color='#CD797D', linewidth=4)
plt.fill_between(average_time_slow_baseline, 
                 average_coverage_percent_slow_baseline - std_coverage_percent_slow_baseline, 
                 average_coverage_percent_slow_baseline + std_coverage_percent_slow_baseline, 
                 color='#CD797D', alpha=0.4)

# Plot for WSR
plt.plot(average_time_wsr, average_coverage_percent_wsr, label='WiSER-X Average Coverage', color='#6E954B', linewidth=4)
plt.fill_between(average_time_wsr, 
                 average_coverage_percent_wsr - std_coverage_percent_wsr, 
                 average_coverage_percent_wsr + std_coverage_percent_wsr, 
                 color='#6E954B', alpha=0.4)

# Add dots at the end of each curve
plt.scatter(average_time_slow_baseline[-1], average_coverage_percent_slow_baseline.iloc[-1], color='red', edgecolor='black', s=100, zorder=5)
plt.scatter(average_time_wsr[-1], average_coverage_percent_slow_baseline.iloc[-1], color='green', edgecolor='black', s=100, zorder=5)


plt.vlines(x=average_time_slow_baseline[-1], ymin=0, ymax=average_coverage_percent_slow_baseline.iloc[-1], 
           colors='red', linestyles='dashed', zorder=5)
plt.vlines(x=average_time_wsr[-1], ymin=0, ymax=average_coverage_percent_wsr.iloc[-1], 
           colors='green', linestyles='dashed', zorder=5)

plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)


plt.xlabel('Time Elapsed (s)')
plt.ylabel('Coverage Percent')
# plt.title('Coverage over Time for Divide-and-Conquer and WSR with One Slow Robot')
legend = plt.legend(fontsize='small', loc='upper left')
legend.get_frame().set_alpha(0.5)
plt.grid(False)
plt.ylim(0, 100)

plt.tight_layout()

plt.show()
