import pandas as pd
from typing import List, Dict, Tuple
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
# 多车调度模型
MAX_CAPACITY = 20

def select_starting_points(bike_counts: Dict[str, int], vehicles: List[Dict], df_distance: pd.DataFrame):
    """为每辆车选择合理的起点并动态计算初始载量 Nc"""
    sorted_stations = sorted(bike_counts.items(), key=lambda x: -x[1])

    for idx, vehicle in enumerate(vehicles):
        start_station = sorted_stations[idx % len(sorted_stations)][0]
        vehicle["location"] = start_station
        calculate_initial_nc(bike_counts, vehicle, MAX_CAPACITY)

def calculate_initial_nc(
        bike_counts: Dict[str, int],
        vehicle: Dict,
        max_capacity: int=20
        ) -> int:
    location = vehicle["location"]
    supply = bike_counts.get(location, 0)
    load = min(supply, max_capacity)
    
    vehicle["Nc"] = load
    bike_counts[location] -= load


def calculate_nij_matrix(
    df_distance: pd.DataFrame,
    bike_counts: Dict[str, int],
    Nc_list: List[int],
    a: float = 0.2,
    b: float = 0.2,
    c: float = 0.2
) -> List[Dict]:
    """计算所有站点对的调度优先级nij（支持多车Nc输入）
    
    参数:
        df_distance: 站点间距离矩阵
        bike_counts: 各站点自行车数量（正为富余，负为短缺）
        Nc_list: 所有调度车的当前载量列表
        a, b, c: 权重参数
    
    返回:
        按nij降序排序的调度对列表
    """
    nij_list = []
    locations = list(bike_counts.keys())
    
    for i in locations:
        for j in locations:
            if i == j:
                continue
            try:
                tij = df_distance.loc[i, j] / 416.7  # 时间（分钟）
                Ni, Nj = bike_counts[i], bike_counts[j]
                
                # 多车情况下选择最优Nc（使nij最大）
                best_nij = -float('inf')
                for Nc in Nc_list:
                    nij = a/tij + b*(Nc-Nj)/25 + c*(2*Nj/(Nc+0.001))/25
                    if nij > best_nij:
                        best_nij = nij
                
                nij_list.append({
                    "from": i, "to": j,
                    "tij": tij, "Ni": Ni, "Nj": Nj,
                    "nij": best_nij
                })
            except KeyError:
                continue
                
    return sorted(nij_list, key=lambda x: x["nij"], reverse=True)


def perform_dispatch(
    i: str,
    j: str,
    Nc: int,
    bike_counts: Dict[str, int],
) -> Tuple[int, int, int]:
    """执行单个调度动作（取车或卸车）
    
    参数:
        i, j: 出发站和目标站
        Nc: 调度车当前载量
        bike_counts: 站点自行车数量字典
    
    返回:
        (更新后的Nc, 取车数量, 卸车数量)
    """
    moved_out = moved_in = 0
    can_pickup = Nc < MAX_CAPACITY
    
    if can_pickup and bike_counts[i] > 0:  # 取车
        moved_out = min(bike_counts[i], MAX_CAPACITY - Nc)
        bike_counts[i] -= moved_out
        Nc += moved_out
    elif bike_counts[i] < 0 and Nc > 0:  # 卸车
        moved_in = min(-bike_counts[i], Nc)
        bike_counts[i] += moved_in
        Nc -= moved_in
    
    if can_pickup and bike_counts[j] > 0:
        moved_out = min(bike_counts[j], MAX_CAPACITY - Nc)
        bike_counts[j] -= moved_out
        Nc += moved_out
    elif bike_counts[j] < 0 and Nc > 0:
        moved_in = min(-bike_counts[j], Nc)
        bike_counts[j] += moved_in
        Nc -= moved_in
    
    return Nc, moved_out, moved_in


def multi_vehicle_dispatch(
    df_distance: pd.DataFrame,
    bike_counts: Dict[str, int],
    num_vehicles: int = 3,
    max_steps: int = 100,
    a: float = 0.2,
    b: float = 0.2,
    c: float = 0.2
) -> pd.DataFrame:
    """多车协同调度主函数
    对于a, b, c参数，这里不再设限制，可以根据实际情况调整
    """
    
    # 初始化车辆状态
    vehicles = [
        {"id": k, "Nc": 0, "location": None, "route": []}
        for k in range(num_vehicles)
    ]
    
    select_starting_points(bike_counts, vehicles, df_distance)
    
    all_routes = []
    step = 0
    
    while step < max_steps:
        step += 1
        
        active_vehicles = [v for v in vehicles if (v["Nc"] < MAX_CAPACITY) or (v["Nc"] > 0)]
        
        if not active_vehicles:
            break
        
        # 计算全局优先级
        Nc_list = [v["Nc"] for v in vehicles]
        nij_sorted = calculate_nij_matrix(df_distance, bike_counts, Nc_list, a, b, c)
        
        for vehicle in active_vehicles:
            current_loc = vehicle["location"]
            valid_pairs = []
            for pair in nij_sorted:
                i, j = pair["from"], pair["to"]
                if i !=current_loc:
                    continue
                if (vehicle["Nc"] < MAX_CAPACITY and bike_counts[i] > 0) or \
                   (vehicle["Nc"] > 0 and bike_counts[j] < 0):
                    valid_pairs.append(pair)
            
            if not valid_pairs:
                continue
            
            best_pair = valid_pairs[0]
            i, j = best_pair["from"], best_pair["to"]
            
            # 执行调度
            Nc_new, moved_out, moved_in = perform_dispatch(i, j, vehicle["Nc"], bike_counts)
            print(f"车辆{vehicle['id']}调度：{i} -> {j}, moved_in： {moved_in}，Nc_new：{Nc_new}")
            vehicle["Nc"] = Nc_new
            vehicle["location"] = j
            vehicle["route"].append({
                "step": step,
                "from": i, 
                "moved_out": moved_out,
                "to": j,
                "moved_in": moved_in,
                "Nc_after": vehicle["Nc"],
                "nij": best_pair["nij"]
            })
    
    # 整理所有车辆的调度记录
    for v in vehicles:
        for r in v["route"]:
            all_routes.append({
                "vehicle_id": v["id"],
                **r
            })
    
    return pd.DataFrame(all_routes)


def plot_vehicle_routes(df_routes, coord_file):
    """
    画出所有调度车经过的路径，只包含实际经过的点。
    
    参数：
    - df_routes: 调度记录 DataFrame，包含 vehicle_id、from、to 等字段
    - coord_file: 坐标 Excel 文件路径，包含 name, x, y 三列
    """
    df_coords = pd.read_excel(coord_file)
    df_coords.set_index("name", inplace=True)

    used_points = set(df_routes['from']).union(set(df_routes['to']))
    df_coords_filtered = df_coords.loc[df_coords.index.intersection(used_points)]

    plt.figure(figsize=(10, 10))

    # 为每辆车画出路径
    for vehicle_id in df_routes["vehicle_id"].unique():
        df_v = df_routes[df_routes["vehicle_id"] == vehicle_id]
        x_vals, y_vals = [], []

        for _, row in df_v.iterrows():
            x_vals.append(df_coords.loc[row["from"], "x"])
            y_vals.append(df_coords.loc[row["from"], "y"])
            x_vals.append(df_coords.loc[row["to"], "x"])
            y_vals.append(df_coords.loc[row["to"], "y"])
        
        plt.plot(x_vals, y_vals, marker='o', label=f"Vehicle {vehicle_id}")

    for name, row in df_coords_filtered.iterrows():
        plt.text(row["x"] + 10, row["y"] + 10, name, fontsize=8)

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Shared Bike Dispatch Routes")
    plt.legend()
    plt.grid(True)
    plt.show()