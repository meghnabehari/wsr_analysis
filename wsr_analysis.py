import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 11


folder_path = 'wsr/time'

files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

data_frames = []

for file in files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    df['time_elapsed'] = df['time_elapsed'].round().astype(int)  # Round and convert to integer
    data_frames.append(df)

avg_termination_time = int(np.mean([df['time_elapsed'].max() for df in data_frames]))

time_range = range(0, avg_termination_time + 1)
avg_df = pd.DataFrame(time_range, columns=['time_elapsed'])

avg_coverage = []
for t in time_range:
    coverage_values = []
    for df in data_frames:
        if t in df['time_elapsed'].values:
            coverage_values.append(df[df['time_elapsed'] == t]['coverage_percent'].values[0])
    if coverage_values:
        avg_coverage.append(np.mean(coverage_values))
    else:
        avg_coverage.append(0)  

avg_df['coverage_percent'] = avg_coverage

plt.figure(figsize=(10, 6))

for i, (df, file) in enumerate(zip(data_frames, files)):
    plt.plot(df['time_elapsed'], df['coverage_percent'], label=f"Trial {i + 1}", alpha=0.5, linewidth=2)

plt.plot(avg_df['time_elapsed'], avg_df['coverage_percent'], label='Average', linestyle='--', color='black', linewidth=3)

plt.xlabel('Time Elapsed')
plt.ylabel('Map Coverage Percent')
plt.title('WSR Map Coverage Percent Over Time')
plt.legend(loc='lower right')
plt.yticks(np.arange(0, 101, 10))
plt.grid(axis='y')
plt.xticks()
plt.grid(True)
plt.show()
