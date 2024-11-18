import pandas as pd
import glob
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 16

# Finds failure coverage percentˆ
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
    
    # Calculate the average failure time
    failure_times = []
    for main_data in all_main_data:
        failure_time = main_data[main_data['coverage_percent'] >= average_failure_coverage]['time_elapsed'].values[0]
        failure_times.append(failure_time)
    
    average_failure_time = sum(failure_times) / len(failure_times)
    
    # Calculate the average total exploration time across all runs
    total_exploration_times = [main_data['time_elapsed'].max() for main_data in all_main_data]
    average_total_exploration_time = sum(total_exploration_times) / len(total_exploration_times)
    
    # Calculate the average terminating coverage
    average_terminating_coverage = sum(terminating_merged_12_coverage) / len(terminating_merged_12_coverage)
    
    return all_main_data, average_failure_time, average_terminating_coverage, average_total_exploration_time

# Calculate WSR and Manual statistics
wsr_data, wsr_failure_time, wsr_terminating_coverage, wsr_avg_termination_time = calculate_average_coverage(
    'wsr_failure_consolidated/time', 
    'wsr_failure_consolidated/failure', 
    'Failure Coverage (%)'
)
manual_data, manual_failure_time, manual_terminating_coverage, manual_avg_termination_time = calculate_average_coverage(
    'manual_failure_consolidated/time', 
    'manual_failure_consolidated/failure', 
    'Manual Failure Coverage (%)'
)

# Calculate the combined average failure time
combined_avg_failure_time = (wsr_failure_time + manual_failure_time) / 2

def compute_average_coverage(all_main_data, combined_avg_failure_time, wsr_avg_termination_time):
    all_times = sorted(list(set(time for main_data in all_main_data for time in main_data['time_elapsed'] if time < 650)))
    
    average_coverage = []
    coverage_std_devs = []

    for time in all_times:
        coverages = []
        for main_data in all_main_data:
            if time <= combined_avg_failure_time:
                valid_times = main_data[main_data['time_elapsed'] <= time]['coverage_percent']
                coverage = valid_times.values[-1] if not valid_times.empty else main_data['coverage_percent'].values[0]
                coverages.append(coverage)
            else:
                valid_times = main_data[main_data['time_elapsed'] <= time]['merged_12_coverage']
                coverage = valid_times.values[-1] if not valid_times.empty else main_data['merged_12_coverage'].values[0]
                coverages.append(coverage)

        average_coverage.append(sum(coverages) / len(coverages))
        coverage_std_devs.append(np.std(coverages))
    
    valid_indices = [i for i, t in enumerate(all_times) if t <= wsr_avg_termination_time]
    valid_times = [all_times[i] for i in valid_indices]
    valid_coverage = [average_coverage[i] for i in valid_indices]
    valid_std_dev = [coverage_std_devs[i] for i in valid_indices]
    
    return valid_times, valid_coverage, valid_std_dev

# Compute coverage values for plotting
wsr_times, wsr_coverage, wsr_std_dev = compute_average_coverage(wsr_data, combined_avg_failure_time, wsr_avg_termination_time)
manual_times, manual_coverage, manual_std_dev = compute_average_coverage(manual_data, combined_avg_failure_time, manual_avg_termination_time)

# PLOTTING

# Custom colors 
wsr_line_color ='#A1C185'
manual_line_color ='#CD797D'
failure_point_color = '#f2cc8f' 

plt.figure(figsize=(10, 6))

# Plot WSR data up to its average termination time
plt.plot(wsr_times, wsr_coverage, label='WSR Coverage Percent', color=wsr_line_color, linewidth=3)
plt.fill_between(wsr_times, 
                 np.array(wsr_coverage) - np.array(wsr_std_dev), 
                 np.array(wsr_coverage) + np.array(wsr_std_dev), 
                 color=wsr_line_color, alpha=0.3)

# Plot Manual data up to its average termination time
plt.plot(manual_times, manual_coverage, label='Manual Coverage Percent', color=manual_line_color, linewidth=3)
plt.fill_between(manual_times, 
                 np.array(manual_coverage) - np.array(manual_std_dev), 
                 np.array(manual_coverage) + np.array(manual_std_dev), 
                 color=manual_line_color, alpha=0.3)

# plt.axvline(x=combined_avg_failure_time, color=failure_point_color, alpha=0.9, linewidth=2)

# Add end points
plt.scatter([wsr_times[-1]], [wsr_coverage[-1]], color='green', s=60, edgecolor='black', zorder=5)
plt.scatter([manual_times[-1]], [manual_coverage[-1]], color='red', s=60, edgecolor='black', zorder=5)

# Add horizontal lines connecting the endpoints to the y-axis
plt.hlines(y=wsr_coverage[-1], xmin=0, xmax=wsr_times[-1], colors='green', linestyles='dashed')
plt.hlines(y=manual_coverage[-1], xmin=0, xmax=manual_times[-1], colors='red', linestyles='dashed')
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)

plt.xlim(0, max(wsr_avg_termination_time, manual_avg_termination_time) + 5)
plt.xlabel('Time Elapsed (s)')
plt.ylabel('Merged Map Coverage Percent')
# plt.title('Map Coverage Recovery')

plt.yticks(np.arange(0, 101, 10)) 
plt.xticks()
# plt.legend(loc='lower left')
plt.show()

wsr_termination_index = np.argmax(np.array(wsr_times) >= wsr_avg_termination_time)

# Get the standard deviation at the WSR termination time
wsr_std_dev_at_termination = wsr_std_dev[wsr_termination_index]

print("Standard Deviation at WSR Termination Time:", wsr_std_dev_at_termination)
print("WSR Average Terminating Merged_12_Coverage:", wsr_terminating_coverage)
print("Manual Average Terminating Merged_12_Coverage:", manual_terminating_coverage)
print("Combined Average Failure Time:", combined_avg_failure_time)
print("WSR Average Termination Time:", wsr_avg_termination_time)
print("Manual Average Termination Time:", manual_avg_termination_time)
