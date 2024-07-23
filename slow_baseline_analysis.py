import os
import pandas as pd
import matplotlib.pyplot as plt

# Base directory structures
base_dir_slow_baseline = "slow_baseline"
base_dir_far_wsr_slow = "far_wsr_slow"
subfolders = ["bottom", "upper_left", "upper_right"]
time_folder = "time"

# Function to get max times for slow_baseline
def get_max_times_slow_baseline(base_dir, subfolders, time_folder):
    max_times = []
    for i in range(10):
        max_time_per_run = []
        for subfolder in subfolders:
            folder_path = os.path.join(base_dir, subfolder, time_folder)
            csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

            # Ensure we process files in the same order across subfolders
            csv_files.sort()

            file_path = os.path.join(folder_path, csv_files[i])
            df = pd.read_csv(file_path)
            max_time = df['time_elapsed'].max()
            max_time_per_run.append(max_time)
        max_times.append(max(max_time_per_run))
    return max_times

# Function to get max times for far_wsr_slow
def get_max_times_far_wsr_slow(base_dir, time_folder):
    max_times = []
    folder_path = os.path.join(base_dir, time_folder)
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    # Ensure we process files in the same order
    csv_files.sort()

    for i in range(10):
        file_path = os.path.join(folder_path, csv_files[i])
        df = pd.read_csv(file_path)
        max_time = df['time_elapsed'].max()
        max_times.append(max_time)
    return max_times

# Get max times for both datasets
max_times_slow_baseline = get_max_times_slow_baseline(base_dir_slow_baseline, subfolders, time_folder)
max_times_far_wsr_slow = get_max_times_far_wsr_slow(base_dir_far_wsr_slow, time_folder)

# Calculate average max times and standard deviations
average_max_time_slow_baseline = sum(max_times_slow_baseline) / len(max_times_slow_baseline)
average_max_time_far_wsr_slow = sum(max_times_far_wsr_slow) / len(max_times_far_wsr_slow)

std_dev_slow_baseline = pd.Series(max_times_slow_baseline).std()
std_dev_far_wsr_slow = pd.Series(max_times_far_wsr_slow).std()

# Plotting the result with different colors
plt.figure(figsize=(10, 6))
categories = ['Divide and Conquer Baseline', 'WSR']
values = [average_max_time_slow_baseline, average_max_time_far_wsr_slow]
error = [std_dev_slow_baseline, std_dev_far_wsr_slow]
colors = ['#CD797D', '#6E954B']

plt.bar(categories, values, yerr=error, capsize=5, width=0.4, color=colors)
plt.ylabel('Time Elapsed')
plt.title('Average Termination Time to Cover 95 Percent of the Map in a Slow Robot Failure Scenario')
plt.show()

print("Average Maximum Time Elapsed (Slow Baseline):", average_max_time_slow_baseline)
print("Average Maximum Time Elapsed (Far WSR Slow):", average_max_time_far_wsr_slow)
