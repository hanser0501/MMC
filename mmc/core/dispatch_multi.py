import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

from sim_dispatch_multi import (
    multi_vehicle_dispatch,
    plot_vehicle_routes
)

distance_file = r"D:\MMC\mmc\data\shortest_matrix.xlsx"
count_file = r"D:\MMC\mmc\data\points_number.xlsx"

df_distance = pd.read_excel(distance_file, index_col=0)
df_counts = pd.read_excel(count_file, sheet_name="Sheet3")
df_counts = df_counts[pd.to_numeric(df_counts["count"], errors='coerce').notnull()]
bike_counts = dict(zip(df_counts['location'], df_counts['count']))

# 调用多车调度
df_result = multi_vehicle_dispatch(
    df_distance=df_distance,
    bike_counts=bike_counts,
    num_vehicles=3,
    max_steps=5
)

result_path = r"D:\MMC\mmc\data\dispatch_result_multi.xlsx"
coord_file = r"D:\MMC\mmc\data\points.xlsx"
df_result.to_excel(result_path, index=False)
plot_vehicle_routes(df_result, coord_file)