import pandas as pd
import glob
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 11

# Finds failure coverage percent
def process_file_pair(main_file, failure_file, failure_column):
    main_data = pd.read_csv(main_file)
    failure_data = pd.read_csv(failure_file)
    
    tb3_robots = failure_data[failure_data['Robot'].isin(['tb3_1', 'tb3_2', 'tb3_3'])]
    failure_coverage = tb3_robots[failure_column].values[0]
    
    return main_data, failure_coverage

def calculate_average_coverage(main_folder, failure_folder, failure_column):
    # Initializations
    main_files = sorted(glob.glob(f'{main_folder}/*.csv'))
    failure_files = sorted(glob.glob(f'{failure_folder}/*.csv'))

    all_main_data = []
    all_failure_coverages = []
    terminating_merged_12_coverage = []

    # Process each pair of main and failure files
    for main_file, failure_file in zip(main_files, failure_files):
        main_data, failure_coverage = process_file_pair(main_file, failure_file, failure_column)
        
        all_main_data.append(main_data)
        all_failure_coverages.append(failure_coverage)
        terminating_merged_12_coverage.append(main_data['merged_12_coverage'].values[-1])

    # Calculate the average failure coverage percentage
    average_failure_coverage = sum(all_failure_coverages) / len(all_failure_coverages)
    
    # Uses average failure percentage to calculate the average failure time
    failure_times = []
    for main_data in all_main_data:
        # Find the time when coverage percent first reaches or exceeds the average failure coverage
        failure_time = main_data[main_data['coverage_percent'] >= average_failure_coverage]['time_elapsed'].values[0]
        failure_times.append(failure_time)

    average_failure_time = sum(failure_times) / len(failure_times)

    # Calculate the average total exploration time across all runs
    total_exploration_times = [main_data['time_elapsed'].max() for main_data in all_main_data]
    average_total_exploration_time = sum(total_exploration_times) / len(total_exploration_times)

    # Collect all unique time values across all runs
    all_times = sorted(list(set(time for main_data in all_main_data for time in main_data['time_elapsed'] if time < 650)))
    
    # Calculate the average coverage for each time step and standard deviation
    average_coverage = []
    coverage_std_devs = []

    for time in all_times:
        coverages = []
        for main_data in all_main_data:
            if time <= average_failure_time:
                # Before average failure time, use 'coverage_percent'
                valid_times = main_data[main_data['time_elapsed'] <= time]['coverage_percent']
                if not valid_times.empty:
                    coverage = valid_times.values[-1]
                else:
                    coverage = main_data['coverage_percent'].values[0]  # Handle case where no valid times found
                coverages.append(coverage)
            else:
                # After average failure time, use 'merged_12_coverage'
                valid_times = main_data[main_data['time_elapsed'] <= time]['merged_12_coverage']
                if not valid_times.empty:
                    coverage = valid_times.values[-1]
                else:
                    coverage = main_data['merged_12_coverage'].values[0]  # Handle case where no valid times found
                coverages.append(coverage)

        # Calculate the average coverage at this time step
        average_coverage.append(sum(coverages) / len(coverages))
        # Calculate the standard deviation of the coverage at this time step
        coverage_std_devs.append(np.std(coverages))
    
    # Calculate the average terminating coverage
    average_terminating_coverage = sum(terminating_merged_12_coverage) / len(terminating_merged_12_coverage)
    
    return all_times, average_coverage, coverage_std_devs, average_failure_time, average_terminating_coverage, average_total_exploration_time


# Calculate plot values for graph
wsr_times, wsr_coverage, wsr_std_dev, wsr_failure_time, wsr_terminating_coverage, wsr_avg_termination_time = calculate_average_coverage('wsr_failure/main', 'wsr_failure/failure', 'Failure Coverage (%)')
manual_times, manual_coverage, manual_std_dev, manual_failure_time, manual_terminating_coverage, manual_avg_termination_time = calculate_average_coverage('manual_failure/main', 'manual_failure/failure', 'Manual Failure Coverage (%)')

# PLOTTING

# Custom colors 
wsr_line_color ='#A1C185'
manual_line_color ='#CD797D'
wsr_failure_point_color = '#f2cc8f' 
manual_failure_point_color = '#f2cc8f'

plt.figure(figsize=(10, 6))

# Plot WSR data up to its average termination time
wsr_valid_indices = [i for i, t in enumerate(wsr_times) if t <= wsr_avg_termination_time]
wsr_valid_times = [wsr_times[i] for i in wsr_valid_indices]
wsr_valid_coverage = [wsr_coverage[i] for i in wsr_valid_indices]
wsr_valid_std_dev = [wsr_std_dev[i] for i in wsr_valid_indices]

plt.plot(wsr_valid_times, wsr_valid_coverage, label='WSR Coverage Percent', 
         color=wsr_line_color, 
         linewidth=3)
plt.fill_between(wsr_valid_times, 
                 np.array(wsr_valid_coverage) - np.array(wsr_valid_std_dev), 
                 np.array(wsr_valid_coverage) + np.array(wsr_valid_std_dev), 
                 color=wsr_line_color, 
                 alpha=0.1)

# Plot Manual data up to its average termination time
manual_valid_indices = [i for i, t in enumerate(manual_times) if t <= manual_avg_termination_time]
manual_valid_times = [manual_times[i] for i in manual_valid_indices]
manual_valid_coverage = [manual_coverage[i] for i in manual_valid_indices]
manual_valid_std_dev = [manual_std_dev[i] for i in manual_valid_indices]

plt.plot(manual_valid_times, manual_valid_coverage, label='Manual Coverage Percent', 
         color=manual_line_color,
         linewidth=3)
plt.fill_between(manual_valid_times, 
                 np.array(manual_valid_coverage) - np.array(manual_valid_std_dev), 
                 np.array(manual_valid_coverage) + np.array(manual_valid_std_dev), 
                 color=manual_line_color, 
                 alpha=0.1)

plt.axvline(x=wsr_failure_time,  color=wsr_failure_point_color, label='WSR Average 1 Robot Failure Point', alpha=0.9, linewidth=2)
plt.axvline(x=manual_failure_time, color=manual_failure_point_color, linestyle='--',label='Manual Average 1 Robot Failure Point', alpha=0.9, linewidth=2)

# Add end points
plt.scatter([wsr_valid_times[-1]], [wsr_valid_coverage[-1]], color='green', s=60, edgecolor='black', zorder=5, label="WSR Termination")
plt.scatter([manual_valid_times[-1]], [manual_valid_coverage[-1]], color='red', s=60, edgecolor='black', zorder=5, label="Manual Termination")

# Add dashed line connecting the endpoints
# plt.plot([wsr_valid_times[-1], manual_valid_times[-1]], 
#          [wsr_valid_coverage[-1], manual_valid_coverage[-1]], 
#          color='black', linestyle='--', linewidth=1)

plt.xlim(0, max(wsr_avg_termination_time, manual_avg_termination_time) + 5)
plt.xlabel('Time Elapsed (s)')
plt.ylabel('Merged Map Coverage Percent')
plt.title('Map Coverage Recovery with Early Failure Points')

plt.yticks(np.arange(0, 101, 10)) 
plt.grid(axis='y')
plt.xticks()

plt.legend()
plt.show()

print("WSR Average Terminating Merged_12_Coverage:", wsr_terminating_coverage)
print("Manual Average Terminating Merged_12_Coverage:", manual_terminating_coverage)
print("WSR Average Termination Time:", wsr_avg_termination_time)
print("Manual Average Termination Time:", manual_avg_termination_time)
