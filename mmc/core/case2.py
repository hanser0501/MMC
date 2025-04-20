import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.gridspec as gridspec

# 设置中文字体，解决乱码问题
plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False

file_path = r'D:\MMC\mmc\data\2.xlsx'
df = pd.read_excel(file_path)
df.columns = df.columns.str.strip()
df.set_index(df.columns[0], inplace=True)
df.dropna(axis=1, how='all', inplace=True)
if '总数' in df.columns:
    df.drop(columns='总数', inplace=True)

df.index = df.index.map(lambda t: t.strftime('%H:%M'))
df.index = pd.to_datetime(df.index, format='%H:%M')
df = df.sort_index()
df.index = df.index.strftime('%H:%M')

groups = {
    "校门": ["东门", "南门", "北门"],
    "食堂": ["一食堂", "二食堂", "三食堂"],
    "宿舍": ["梅苑1栋", "菊苑1栋"],
    "教学楼": ["教学2楼", "教学4楼", "计算机学院", "工程中心"],
    "运动生活": ["网球场", "体育馆", "校医院"]
}

fig = plt.figure(figsize=(18, 12))
gs = gridspec.GridSpec(3, 2, figure=fig, hspace=1, wspace=0.3)

# 创建子图
for i, (group_name, locations) in enumerate(groups.items(), 1):
    ax = fig.add_subplot(gs[i-1])
    
    for loc in locations:
        if loc in df.columns:
            ax.plot(df.index, df[loc], marker='o', label=loc)
    plt.title(group_name, fontsize=14)
    plt.xlabel("时间")
    plt.ylabel("单车数量")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)
plt.suptitle("各区域时间段单车数量改变趋势", fontsize=20, y=0.98)
plt.show()