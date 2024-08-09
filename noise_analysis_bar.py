import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams


folders = ["2_1", "5_10", "10_20", "30_100"]
main_directory = ""
rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman'] 
rcParams['font.size'] = 12

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


# Plot the results as a bar graph
plt.figure(figsize=(10, 6))

# Custom colors
colors = ["#5B838F","#CD797D","#F5D787",  "#F6B379",  ]

bar_width = 0.15  # Width of the bars
bar_positions = np.arange(len(folders))  # Positions for the bars

avg_termination_times = [completion_times[folder] for folder in folders]
avg_coverages_at_termination = [avg_coverage[folder][int(avg_termination_times[i])] for i, folder in enumerate(folders)]
std_coverages_at_termination = [std_coverage[folder][int(avg_termination_times[i])] for i, folder in enumerate(folders)]

# Sort data in descending order based on average coverage
sorted_indices = np.argsort(avg_coverages_at_termination)[::-1]
sorted_folders = [folders[i] for i in sorted_indices]
sorted_avg_coverages = [avg_coverages_at_termination[i] for i in sorted_indices]
sorted_std_coverages = [std_coverages_at_termination[i] for i in sorted_indices]
sorted_colors = [colors[i] for i in sorted_indices]

# Plot the results as a bar graph
plt.figure(figsize=(8, 6))  # Adjust the figure size for better fitting

# Increase bar width to fill space
bar_width = 0.8  # Further increased for even less white space
bar_positions = np.arange(len(folders))  # Positions for the bars

# Plot bars
plt.bar(bar_positions, sorted_avg_coverages, bar_width, color=sorted_colors, 
        yerr=sorted_std_coverages, capsize=5, alpha=0.8)

# Parse the folder name for the x-tick labels
xtick_labels = [f"{folder.split('_')[0]} deg, {folder.split('_')[1]} cm" for folder in sorted_folders]
plt.xticks(bar_positions, xtick_labels)

plt.yticks(np.arange(0, 101, 10))

plt.xlabel('WSR Noise Level', labelpad=20)  # Increase labelpad for more space
plt.ylabel('Merged Map Coverage Percent at Termination Time')
plt.title('Map Coverage at Termination Time with Varying WSR Noise')

plt.show()

