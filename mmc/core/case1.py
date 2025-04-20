import pandas as pd
import math
import heapq
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl

# 设置中文字体，解决乱码问题
mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'STHeiti'] 
mpl.rcParams['axes.unicode_minus'] = False

# 读取 Excel 数据
points_path = r"D:\MMC\mmc\core\points.xlsx"
edges_path = r"D:\MMC\mmc\core\edges.xlsx"
df_points = pd.read_excel(points_path, sheet_name="Sheet1")
df_edges = pd.read_excel(edges_path, sheet_name="Sheet1")

points = {row["name"]: (row["x"], row["y"]) for _, row in df_points.iterrows()}
edges = [(row["from"], row["to"]) for _, row in df_edges.iterrows()]

# 计算距离
def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def build_graph(points, edges):
    graph = {name: [] for name in points}
    for name1, name2 in edges:
        dist = euclidean_distance(points[name1], points[name2])
        graph[name1].append((name2, dist))
        graph[name2].append((name1, dist))
    return graph

graph = build_graph(points, edges)

# Dijkstra 算法：从一个点出发，对每一个点找最短距离，并进行比较，找所有最短路径
def dijkstra_all(graph, start):
    queue = [(0, start)]
    distances = {node: float('inf') for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0

    while queue:
        current_dist, current_node = heapq.heappop(queue)

        for neighbor, weight in graph[current_node]:
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    return distances, previous

# 所有两点之间最短路径距离保存
all_shortest = []
for start in points:
    distances, _ = dijkstra_all(graph, start)
    for end in points:
        if start != end:
            all_shortest.append({
                "From": start,
                "To": end,
                "Distance": distances[end]
            })

df_shortest = pd.DataFrame(all_shortest)

place_names = list(points.keys())
distance_matrix = pd.DataFrame(index=place_names, columns=place_names)

for start in place_names:
    distances, _ = dijkstra_all(graph, start)
    for end in place_names:
        distance_matrix.loc[start, end] = round(distances[end], 2)
#print(df_shortest.head())  # 可选：查看前几行结果
#output_path = r"D:\MMC\mmc\data\shortest.xlsx"
#df_shortest.to_excel(output_path, index=False)  # 保存结果到 Excel 文件
#output_matrix_path = r"D:\MMC\mmc\data\shortest_matrix.xlsx"
#distance_matrix.to_excel(output_matrix_path)

def rotate_coords(points_dict):
    return {name: (-y, x) for name, (x, y) in points_dict.items()}
'''
可视化：画点图和路径图
这里逆时针旋转坐标系90度，使得图形能完整输出
'''
# 替换原有 pos
rotated_points = rotate_coords(points)

# 构建 NetworkX 图
G = nx.Graph()
for name, coord in rotated_points.items():
    G.add_node(name, pos=coord)

for name1, name2 in edges:
    dist = euclidean_distance(points[name1], points[name2])  # 原始距离
    G.add_edge(name1, name2, weight=round(dist, 2))

# 画图（使用旋转后的位置）
pos = nx.get_node_attributes(G, 'pos')
plt.figure(figsize=(10, 8))
nx.draw(G, pos, with_labels=True, node_color='lightgreen', node_size=600, font_size=10)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8)
plt.title("最短路径图（已旋转90°）")
plt.axis("equal")
plt.tight_layout()
plt.show()
"""

G = nx.Graph()

# 添加节点及其坐标
for name, coord in points.items():
    G.add_node(name, pos=coord)

# 添加边及距离作为权重
for name1, name2 in edges:
    dist = euclidean_distance(points[name1], points[name2])
    G.add_edge(name1, name2, weight=round(dist, 2))

pos = nx.get_node_attributes(G, 'pos')
plt.figure(figsize=(10, 8))
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500, font_size=10)
labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8)
plt.title("路径图（边权为距离）")
plt.axis("equal")
plt.tight_layout()
plt.show()
# 转换为矩阵形式
pivot_table = df_shortest.pivot(index="From", columns="To", values="Distance")

plt.figure(figsize=(12, 10))
sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="coolwarm", linewidths=.5)
plt.title("所有点对之间最短距离热力图")
plt.show()

"""