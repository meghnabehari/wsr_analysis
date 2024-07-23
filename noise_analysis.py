import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams


folders = ["2_1", "5_10", "10_20", "30_100"]
main_directory = ""
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman'] 
rcParams['font.size'] = 11

completion_times = {}
coverage_data = {}

# Read the files and calculate average completion times
for folder in folders:
    time_folder = os.path.join(main_directory, folder, "time")
    time_files = sorted([f for f in os.listdir(time_folder) if f.endswith('.csv')])

    times = []
    coverages = []

    for time_file in time_files:
        # Read the time file
        time_df = pd.read_csv(os.path.join(time_folder, time_file))

        # Get the last value of time_elapsed
        last_time = time_df["time_elapsed"].values[-1]
        times.append(last_time)

        # Get coverage_percent data and filter out non-positive values
        total_coverage = time_df["coverage_percent"].values
        total_coverage = np.where(total_coverage > 0, total_coverage, np.nan)  # Replace non-positive values with NaN
        coverages.append(total_coverage)

    # Calculate average completion time
    avg_completion_time = np.mean(times)
    completion_times[folder] = avg_completion_time

    # Store coverage data
    coverage_data[folder] = np.array(coverages)

# Initialize lists to store the results for plotting
avg_coverage = {}
std_coverage = {}

# Calculate average and std of coverage for each time step up to the average completion time
for folder in folders:
    avg_time = completion_times[folder]
    coverages = coverage_data[folder]

    # Calculate the number of steps up to the average completion time
    time_steps = np.arange(0, avg_time, step=1.0)

    avg_coverage[folder] = []
    std_coverage[folder] = []

    for step in time_steps:
        step_coverages = []

        for run in coverages:
            # Ensure we only consider positive coverage values
            if step < len(run) and not np.isnan(run[int(step)]):
                step_coverages.append(run[int(step)])

        if step_coverages:
            avg_coverage[folder].append(np.nanmean(step_coverages))
            std_coverage[folder].append(np.nanstd(step_coverages))
        else:
            avg_coverage[folder].append(0)
            std_coverage[folder].append(0)

# Plot the results
plt.figure(figsize=(10, 6))

# Custom colors
colors = ["#F6B379", "#CD797D", "#A1C185", "#5B838F",]

for folder, color in zip(folders, colors):
    time_steps = np.arange(0, len(avg_coverage[folder]))
    # Parse the folder name for the label
    num1, num2 = folder.split('_')
    label = f"{num1} deg, {num2} cm"
    plt.plot(time_steps, avg_coverage[folder], label=label, color=color, linewidth=2.5)
    plt.fill_between(time_steps, 
                     np.array(avg_coverage[folder]) - np.array(std_coverage[folder]),
                     np.array(avg_coverage[folder]) + np.array(std_coverage[folder]), 
                     color=color, alpha=0.1)

plt.yticks(np.arange(0, 101, 10)) 

plt.xlabel('Time Elapsed (s)')
plt.ylabel('Merged Map Coverage Percent')
plt.title('Coverage Over Time with Varying WSR Noise')
plt.legend(loc='lower right')
plt.grid(axis='y')
plt.show()