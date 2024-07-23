import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 11

folder_path = 'wsr_slow/time'
files = os.listdir(folder_path)
csv_files = [f for f in files if f.endswith('.csv')]

# Sort files based on the ending digit
csv_files.sort(key=lambda x: int(re.search(r'(\d+)\.csv$', x).group(1)))

slow_robot_list = [2, 2, 3, 3, 1, 1, 2, 3, 1, 2]

termination_times_slow = []
termination_times_fast_1 = []
termination_times_fast_2 = []
data_frames = []

total_coverage_sum = np.zeros(1000)
total_coverage_sum_sq = np.zeros(1000)
total_coverage_count = np.zeros(1000)

# Read all files and collect data
for idx, file in enumerate(csv_files):
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    slow_robot = slow_robot_list[idx]

    # Append data frames
    data_frames.append((df, slow_robot))

    # Collect termination times based on slow and fast robots
    slow_termination_time = df['time_elapsed'][df[f'r_{slow_robot}_per'] > 0].max()
    termination_times_slow.append(slow_termination_time)

    # Identify fast robots and split between fast_1 and fast_2
    fast_robots = [r for r in [1, 2, 3] if r != slow_robot]

    fast_1_termination_time = df['time_elapsed'][df[f'r_{fast_robots[0]}_per'] > 0].max()
    termination_times_fast_1.append(fast_1_termination_time)

    fast_2_termination_time = df['time_elapsed'][df[f'r_{fast_robots[1]}_per'] > 0].max()
    termination_times_fast_2.append(fast_2_termination_time)

# Calculate average termination times
avg_termination_time_slow = np.mean(termination_times_slow)
avg_termination_time_fast_1 = np.mean(termination_times_fast_1)
avg_termination_time_fast_2 = np.mean(termination_times_fast_2)

# Create time vectors with steps for each
time_steps_slow = np.linspace(0, avg_termination_time_slow, num=1000)
time_steps_fast_1 = np.linspace(0, avg_termination_time_fast_1, num=1000)
time_steps_fast_2 = np.linspace(0, avg_termination_time_fast_2, num=1000)

# Initialize arrays to accumulate the interpolated values and their squares
slow_sum = np.zeros_like(time_steps_slow)
slow_sum_sq = np.zeros_like(time_steps_slow)
fast_1_sum = np.zeros_like(time_steps_fast_1)
fast_1_sum_sq = np.zeros_like(time_steps_fast_1)
fast_2_sum = np.zeros_like(time_steps_fast_2)
fast_2_sum_sq = np.zeros_like(time_steps_fast_2)
count_slow = np.zeros_like(time_steps_slow)
count_fast_1 = np.zeros_like(time_steps_fast_1)
count_fast_2 = np.zeros_like(time_steps_fast_2)

# Determine the maximum of the average termination times for the total coverage time vector
max_avg_termination_time = max(avg_termination_time_slow, avg_termination_time_fast_1, avg_termination_time_fast_2)
time_steps_total_coverage = np.linspace(0, max_avg_termination_time, num=1000)

# Interpolate data for each file and accumulate
for df, slow_robot in data_frames:

    # Interpolate and accumulate for slow robot
    slow_interp = np.interp(time_steps_slow, df['time_elapsed'], df[f'r_{slow_robot}_per'])
    mask_slow = slow_interp > 0
    slow_sum[mask_slow] += slow_interp[mask_slow]
    slow_sum_sq[mask_slow] += slow_interp[mask_slow] ** 2
    count_slow[mask_slow] += 1

    # Identify fast robots and interpolate
    fast_robots = [r for r in [1, 2, 3] if r != slow_robot]

    fast_1_interp = np.interp(time_steps_fast_1, df['time_elapsed'], df[f'r_{fast_robots[0]}_per'])
    mask_fast_1 = fast_1_interp > 0
    fast_1_sum[mask_fast_1] += fast_1_interp[mask_fast_1]
    fast_1_sum_sq[mask_fast_1] += fast_1_interp[mask_fast_1] ** 2
    count_fast_1[mask_fast_1] += 1

    fast_2_interp = np.interp(time_steps_fast_2, df['time_elapsed'], df[f'r_{fast_robots[1]}_per'])
    mask_fast_2 = fast_2_interp > 0
    fast_2_sum[mask_fast_2] += fast_2_interp[mask_fast_2]
    fast_2_sum_sq[mask_fast_2] += fast_2_interp[mask_fast_2] ** 2
    count_fast_2[mask_fast_2] += 1

    coverage_interp = np.interp(time_steps_total_coverage, df['time_elapsed'], df['coverage_percent'])
    total_coverage_sum += coverage_interp
    total_coverage_sum_sq += coverage_interp ** 2
    total_coverage_count[coverage_interp > 0] += 1

# Avoid division by zero
count_slow[count_slow == 0] = 1
count_fast_1[count_fast_1 == 0] = 1
count_fast_2[count_fast_2 == 0] = 1
total_coverage_count[total_coverage_count == 0] = 1

# Calculate means
slow_avg = slow_sum / count_slow
fast_1_avg = fast_1_sum / count_fast_1
fast_2_avg = fast_2_sum / count_fast_2
total_coverage_avg = total_coverage_sum / total_coverage_count

# Calculate standard deviations
slow_std = np.sqrt((slow_sum_sq / count_slow) - slow_avg ** 2)
fast_1_std = np.sqrt((fast_1_sum_sq / count_fast_1) - fast_1_avg ** 2)
fast_2_std = np.sqrt((fast_2_sum_sq / count_fast_2) - fast_2_avg ** 2)
total_coverage_std = np.sqrt((total_coverage_sum_sq / total_coverage_count) - total_coverage_avg ** 2)

plt.figure(figsize=(12, 8))

slow_line_color = '#CD797D'
fast_line_color_1 = '#6E954B'
fast_line_color_2 = '#5B838F'
total_map = '#F6B379'


plt.plot(time_steps_total_coverage, total_coverage_avg, color=total_map, linewidth=2.5, label='Total Map Coverage', linestyle='--')
plt.fill_between(time_steps_total_coverage, total_coverage_avg - total_coverage_std, total_coverage_avg + total_coverage_std, color=total_map, alpha=0.1)

plt.plot(time_steps_fast_1, fast_1_avg, color=fast_line_color_1, linewidth=2.5,label='Fast Robot #1')
plt.fill_between(time_steps_fast_1, fast_1_avg - fast_1_std, fast_1_avg + fast_1_std, color=fast_line_color_1, linewidth=2, alpha=0.2)

plt.plot(time_steps_fast_2, fast_2_avg, color=fast_line_color_2, linewidth=2.5, label='Fast Robot #2')
plt.fill_between(time_steps_fast_2, fast_2_avg - fast_2_std, fast_2_avg + fast_2_std, color=fast_line_color_2, linewidth=2, alpha=0.2)


plt.plot(time_steps_slow, slow_avg, color=slow_line_color, linewidth=2.5, label='Slow Robot')
plt.fill_between(time_steps_slow, slow_avg - slow_std, slow_avg + slow_std, color=slow_line_color, alpha=0.2)

plt.xlabel('Time Elapsed (s)')
plt.ylabel('Map Coverage Percent')
plt.title('Map Coverage, Slow Robots vs Fast Robots')
plt.yticks(np.arange(0, 101, 10)) 
plt.grid(axis='y')
plt.xticks()
plt.legend(loc='lower right')

plt.show()
