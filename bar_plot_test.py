import matplotlib.pyplot as plt
import numpy as np

# Data for Slow Robot Scenario
labels_slow = ['Divide-and-Conquer Baseline', 'WSR Exploration']
avg_termination_time = [488, 342]

# Data for Failed Robot Scenario
labels_failed = ['No Recovery Baseline', 'WSR Recovery']
avg_map_coverage = [82, 91]

# Create subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Horizontal bar plot for Slow Robot Scenario
ax1.barh(labels_slow, avg_termination_time, color=['#D4AC2B', '#2980B9'], height=0.4)
ax1.set_title('Slow Robot Scenario')
ax1.set_xlabel('Avg Termination Time (s)')
ax1.invert_yaxis()  # To have Divide-and-Conquer Baseline on top

# Highlight that WSR Exploration is lower
ax1.annotate('Lower', xy=(350, 1), xytext=(400, 1.1),
             arrowprops=dict(facecolor='black', shrink=0.05),
             horizontalalignment='center', verticalalignment='bottom')

# Horizontal bar plot for Failed Robot Scenario
ax2.barh(labels_failed, avg_map_coverage, color=['#D4AC2B', '#2980B9'], height=0.4)
ax2.set_title('Failed Robot Scenario')
ax2.set_xlabel('Avg Map Coverage Percent at Termination (%)')
ax2.invert_yaxis()  # To have No Recovery Baseline on top

# Highlight that WSR Recovery is higher
ax2.annotate('Higher', xy=(85, 1), xytext=(80, 1.1),
             arrowprops=dict(facecolor='black', shrink=0.05),
             horizontalalignment='center', verticalalignment='bottom')

# Adjust layout
plt.tight_layout()

# Show plot
plt.show()
