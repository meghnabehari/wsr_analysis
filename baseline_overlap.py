import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.family'] = 'serif'
rcParams['font.serif'] = ['Times New Roman']
rcParams['font.size'] = 11

# folders = {
#     'Baseline 1: Independent': 'hw_baseline_1',
#     'Baseline 2: Oracle': 'hw_baseline_2',
#     'WSR': 'hw_wsr'
# }

# colors = {
#     'Baseline 1: Independent': '#CD797D',
#     'Baseline 2: Oracle': '#5B838F',
#     'WSR': '#6E954B'
# }

folders = {
    'Baseline 1: Independent': 'hw_baseline_loc_3',
    'Baseline 2: Oracle': 'hw_env_1_baseline_2_loc_3',
    'WSR': 'hw_wsr_loc_3'
}

colors = {
    'Baseline 1: Independent': '#CD797D',
    'Baseline 2: Oracle': '#5B838F',
    'WSR': '#6E954B'
}

def read_coverage_data(folder):
    coverage_data = []
    for file_name in os.listdir(os.path.join(folder, 'coverage')):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder, 'coverage', file_name)
            df = pd.read_csv(file_path)
            df['Time Elapsed (s)'] = df['Time Elapsed (s)'].round()
            df['Coverage Overlap (%)'] = df['Coverage Overlap (%)'].apply(lambda x: 5 if x <= 0 else x)
            coverage_data.append(df[['Time Elapsed (s)', 'Coverage Overlap (%)']])
    combined_coverage_df = pd.concat(coverage_data, ignore_index=True)
    return combined_coverage_df

def read_time_data(folder):
    time_data = []
    for file_name in os.listdir(os.path.join(folder, 'time')):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder, 'time', file_name)
            df = pd.read_csv(file_path)
            df['time_elapsed'] = df['time_elapsed'].round()
            df['coverage_percent'] = df['coverage_percent'].round()
            time_data.append(df[['time_elapsed', 'coverage_percent']])
    combined_time_df = pd.concat(time_data, ignore_index=True)
    return combined_time_df

def process_folder(folder):
    coverage_df = read_coverage_data(folder)
    time_df = read_time_data(folder)
    
    merged_df = pd.merge(coverage_df, time_df, left_on='Time Elapsed (s)', right_on='time_elapsed')
    
    # Drop the duplicate time_elapsed column
    merged_df.drop(columns=['time_elapsed'], inplace=True)
    
    # Group by coverage_percent and calculate the mean and standard deviation of coverage overlap
    grouped_df = merged_df.groupby('coverage_percent')['Coverage Overlap (%)'].agg(['mean', 'std']).reset_index()
    
    # Filter the dataframe to include only coverage_percent between 10 and 90
    filtered_df = grouped_df[(grouped_df['coverage_percent'] >= 10) & (grouped_df['coverage_percent'] <= 90)]
    
    return filtered_df

# Process each folder and store the results in a dictionary
results = {}
for name, folder in folders.items():
    results[name] = process_folder(folder)

# Plot coverage percent vs average coverage overlap with standard deviation shading for each dataset
plt.figure(figsize=(10, 6))

for name, df in results.items():
    mean_capped = np.minimum(df['mean'], 100)
    std_capped = np.minimum(df['std'], 100 - mean_capped)
    
    plt.plot(df['coverage_percent'], mean_capped, label=f'{name}', color=colors[name], linewidth=2)
    plt.fill_between(df['coverage_percent'], mean_capped - std_capped, mean_capped + std_capped, color=colors[name], alpha=0.2)

plt.xlabel('Total Map Coverage Percent')
plt.ylabel('Average Coverage Overlap (%)')
plt.title('Robot Map Coverage Overlap, Hardware Loc 3')
plt.legend()
plt.grid(axis='y')
plt.xticks()
# plt.ylim(0, 100) 
plt.show()
