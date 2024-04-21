import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read the CSV file
file_path = "task_durations_and_time_range_per_iteration_and_worker.csv"
df = pd.read_csv(file_path)

# Drop unnecessary columns
df.drop(['Worker_bim_element_name', 'iteration','iterations', 'first_datetime', 'last_datetime', 'duration_difference_minutes'], axis=1, inplace=True)

# Melt the DataFrame to have task durations as values in a single column
melted_df = df.melt(var_name='Task', value_name='Duration')

# Convert 'Duration' column to numeric
melted_df['Duration'] = pd.to_numeric(melted_df['Duration'], errors='coerce')

# Plot a single box plot showing durations for each task
plt.figure(figsize=(12, 6))
sns.boxplot(x='Task', y='Duration', data=melted_df.dropna())  # Drop rows with NaN values
plt.title('Box plot of Task Durations')
plt.xlabel('Task')
plt.ylabel('Duration (minutes)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Read the CSV file
file_path = "task_durations_and_time_range_per_iteration_and_worker.csv"
df = pd.read_csv(file_path)

# # Drop unnecessary columns
# df.drop(['Worker_bim_element_name', 'iteration', 'first_datetime', 'last_datetime', 'duration_difference_minutes'], axis=1, inplace=True)
#
# # Melt the DataFrame to have task durations as values in a single column
# melted_df = df.melt(id_vars='Worker_bim_element_name', value_name='Duration')

# # Convert 'Duration' column to numeric
# melted_df['Duration'] = pd.to_numeric(melted_df['Duration'], errors='coerce')

# Plot box plots for each BIM element
plt.figure(figsize=(12, 6))
sns.boxplot(x='Worker_bim_element_name', y='duration_difference_minutes', data=df)  # Drop rows with NaN values
plt.title('Box plot of Task Durations for Each BIM Element')
plt.xlabel('BIM Element')
plt.ylabel('Duration (minutes)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
