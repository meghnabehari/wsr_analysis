import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

main_folder_slow_baseline = "slow_baseline"
sub_folders = ["bottom", "upper_left", "upper_right"]

def extract_number(filename):
    return int(filename.split('_')[-1].split('.')[0])

all_total_coverages = []
termination_times = []

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

    max_time = int(max(df.index.max() for df in region_coverage.values()))  # Ensure max_time is an integer
    termination_times.append(max_time)

    for region, df in region_coverage.items():
        region_coverage[region] = df.reindex(range(0, max_time + 1)).ffill()

    total_coverage = sum(region_coverage.values())
    total_coverage = total_coverage.reset_index()
    total_coverage = total_coverage[total_coverage['coverage_percent'] <= 99]

    all_total_coverages.append(total_coverage.set_index('time_elapsed')['coverage_percent'])

# Calculate the average total time across all runs
average_total_time = int(np.mean(termination_times))

# Reindex all runs to the average total time, filling missing values with the last available data
aligned_coverages = pd.concat([df.reindex(range(0, average_total_time + 1)).ffill().fillna(0) for df in all_total_coverages], axis=1)

# Calculate the average and standard deviation of coverage percent at each time step
average_coverage_percent = aligned_coverages.mean(axis=1)
std_coverage_percent = aligned_coverages.std(axis=1)

# Plot the average coverage percent with standard deviation
plt.figure(figsize=(10, 6))
plt.plot(average_coverage_percent.index, average_coverage_percent, label='Average Coverage Percent')
plt.fill_between(average_coverage_percent.index, 
                 average_coverage_percent - std_coverage_percent, 
                 average_coverage_percent + std_coverage_percent, 
                 color='b', alpha=0.2, label='Standard Deviation')

plt.xlabel('Time Elapsed (s)')
plt.ylabel('Coverage Percent')
plt.title('Average Coverage Percent vs. Time Elapsed with Standard Deviation')
plt.legend()
plt.grid(True)
plt.ylim(0, 100)
plt.show()
