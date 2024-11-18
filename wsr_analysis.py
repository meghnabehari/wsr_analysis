import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.cm as cm

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 17

# Set the folder path
folder_path = 'wsr_near_far/time'

# List all CSV files in the folder
files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Load all data frames
data_frames = []
for file in files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    df['time_elapsed'] = df['time_elapsed'].round().astype(int)  # Round and convert to integer
    data_frames.append(df)

# Calculate the average termination coverage percent
termination_coverage = [df['coverage_percent'].max() for df in data_frames]
avg_termination_coverage = np.mean(termination_coverage)

# Calculate the average time elapsed
termination_times = [df['time_elapsed'].max() for df in data_frames]
avg_time_elapsed = int(np.mean(termination_times))

# Function to extrapolate the coverage to the average termination coverage and time
def extrapolate_coverage(df, avg_time_elapsed, avg_termination_coverage):
    max_time = df['time_elapsed'].max()
    max_coverage = df['coverage_percent'].max()
    
    if max_coverage < avg_termination_coverage and max_time < avg_time_elapsed:
        slope = (avg_termination_coverage - max_coverage) / (avg_time_elapsed - max_time)
        extrapolated_time = list(range(max_time, avg_time_elapsed + 1))
        extrapolated_coverage = [max_coverage + slope * (t - max_time) for t in extrapolated_time]
        extrapolated_df = pd.DataFrame({'time_elapsed': extrapolated_time, 'coverage_percent': extrapolated_coverage})
        df = pd.concat([df, extrapolated_df.iloc[1:]], ignore_index=True)
    elif max_time < avg_time_elapsed:
        extrapolated_time = list(range(max_time, avg_time_elapsed + 1))
        extrapolated_coverage = [max_coverage] * len(extrapolated_time)
        extrapolated_df = pd.DataFrame({'time_elapsed': extrapolated_time, 'coverage_percent': extrapolated_coverage})
        df = pd.concat([df, extrapolated_df.iloc[1:]], ignore_index=True)
    return df

# Extrapolate data for each trial
extrapolated_data_frames = [extrapolate_coverage(df, avg_time_elapsed, avg_termination_coverage) for df in data_frames]

# Calculate the average coverage over time
time_range = range(0, avg_time_elapsed + 1)
avg_coverage = []
for t in time_range:
    coverage_values = [df[df['time_elapsed'] == t]['coverage_percent'].values[0] for df in extrapolated_data_frames if t in df['time_elapsed'].values]
    avg_coverage.append(np.mean(coverage_values))

# Prepare the average dataframe for plotting
avg_df = pd.DataFrame({
    'time_elapsed': time_range,
    'coverage_percent': avg_coverage
})

coverage_stdev = np.std(termination_coverage)

# Plotting
plt.figure(figsize=(10, 6))
colors = cm.RdYlGn(np.linspace(0, 1, len(extrapolated_data_frames)))

for i, (df, file) in enumerate(zip(extrapolated_data_frames, files)):
    plt.plot(df['time_elapsed'], df['coverage_percent'], color=colors[i], alpha=0.35, linewidth=3)

# Plot the average line
plt.plot(avg_df['time_elapsed'], avg_df['coverage_percent'], linestyle='--', label='Average Exploration Trajectory', color='black', linewidth=3)

# Draw the horizontal line from the termination point to the y-axis
xlim_val = avg_df['time_elapsed'].iloc[-1] + 200
plt.hlines(y=avg_coverage[-1], xmin=0, xmax=avg_df['time_elapsed'].iloc[-1], colors='black', linewidth=3, alpha=0.75, label="Observed Average Termination Coverage Percent")


plt.errorbar(
    x=[avg_df['time_elapsed'].iloc[-1]], 
    y=[avg_coverage[-1]], 
    yerr=coverage_stdev, 
    fmt='o', 
    color='black', 
    ecolor='black', 
    elinewidth=4, 
    capsize=6,
    capthick=3,
    label='Observed Termination Coverage Std Dev'
)

plt.hlines(y=95.0, xmin=0, xmax=xlim_val, colors='red', linewidth=3, alpha=0.65, label="Expected Average Termination Coverage Percent")

# Add a dot at the termination point with error bar

plt.xlabel('Time Elapsed (s)')
plt.ylabel('Map Coverage Percent')
plt.yticks(np.arange(0, 105, 10))

# Ensure the lines extend all the way to the edges, with the bottom left as the origin
plt.xlim(0, xlim_val)
plt.ylim(0, 105)
legend = plt.legend(fontsize='small', loc='lower right')
legend.get_frame().set_alpha(0.5)

plt.show()

# Print the average termination time, standard deviation, and average map coverage at termination
print(f"Average Termination Time: {avg_time_elapsed} s")
print(f"Standard Deviation of Termination Times: {np.std(termination_times):.2f} s")
print(f"Average Map Coverage at Termination: {avg_termination_coverage:.2f}%")
print(f"Standard Deviation of Map Coverage at Termination: {coverage_stdev:.2f}%")