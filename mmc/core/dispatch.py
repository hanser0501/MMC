import pandas as pd
import math
import matplotlib.pyplot as plt
import sys

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

from sim_dispatch import (
    simulate_dispatch_from_nij
)

distance_file = r"D:\MMC\mmc\data\shortest_matrix.xlsx"
count_file = r"D:\MMC\mmc\data\points_number.xlsx"

df_distance = pd.read_excel(distance_file, index_col=0)
df_counts = pd.read_excel(count_file, sheet_name="Sheet1")
df_counts = df_counts[pd.to_numeric(df_counts["count"], errors='coerce').notnull()]
bike_counts = dict(zip(df_counts['location'], df_counts['count']))

result = simulate_dispatch_from_nij(df_distance, bike_counts, Nc_init=0, max_steps=10)
result_df = pd.DataFrame(result)
result_df.to_excel(r"D:\MMC\mmc\data\dispatch_result.xlsx", index=False)