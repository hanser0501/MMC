import pandas as pd

'''
这里运行结果会出现step1从车源充足点到不足点的情况，是因为没有设置出发点
Nc不能及时更新，所以在第一步判断时，Nc为默认值0，使得调度车对于补充车辆的优先级高
优化模型可参考dispatch_sim_tri.py中的select_starting_points
'''

def calculate_nij_matrix(df_distance, bike_counts, Nc, a, b, c):
    nij_list = []
    locations = list(bike_counts.keys())
    counts = list(bike_counts.values())
    df_distance = df_distance.loc[locations]
    
    for i in locations:
        for j in locations:
            if i == j:
                continue
            try:
                tij = df_distance.loc[i, j] / 416.7  # m/min
                Ni = bike_counts[i]
                Nj = bike_counts[j]
                nij = a / tij + b * (Ni - Nj) / 25 + c * (2*Nj / (Nc+0.001)) / 25
                nij_list.append({
                    "from": i,
                    "to": j,
                    "tij": tij,
                    "Ni": Ni,
                    "Nj": Nj,
                    "Nc": Nc,
                    "nij": nij
                })
            except KeyError:
                continue

    return sorted(nij_list, key=lambda x: x["nij"], reverse=True)

def perform_dispatch(i, j, Nc, bike_counts, max_capacity=20):
    N_i = bike_counts[i]
    N_j = bike_counts[j]
    moved_out = moved_in = 0
    if Nc <= max_capacity and N_i > 0: # 补充车辆
        moved_out = min(N_i, max_capacity - Nc)
        bike_counts[i] -= moved_out
        Nc += moved_out
    elif N_i < 0 and Nc > 0: # 供应车辆
        moved_in = min(-N_i, Nc)
        bike_counts[i] += moved_in
        Nc -= moved_in
    if Nc <= max_capacity and N_j > 0: # 补充车辆
        moved_out = min(N_j, max_capacity - Nc)
        bike_counts[j] -= moved_out
        Nc += moved_out
    elif N_j < 0 and Nc > 0: # 供应车辆
        moved_in = min(-N_j, Nc)
        bike_counts[j] += moved_in
        Nc -= moved_in
    
    return Nc, moved_out, moved_in

def simulate_dispatch_from_nij(df_distance, bike_counts, a=0.2, b=0.2, c=0.2, Nc_init=0, max_steps=10, max_capacity=20, start_point=None):
    Nc = Nc_init
    route = []

    # 如果没有指定起点，根据 nij 最大值自动选择
    if start_point is None:
        nij_init = calculate_nij_matrix(df_distance, bike_counts, Nc, a, b, c)
        print(nij_init[0]["from"])
        if not nij_init:
            print("没有可用的调度路径。")
            return pd.DataFrame()
        start_point = nij_init[0]["from"]

    current_location = start_point

    for step in range(max_steps):
        nij_sorted = calculate_nij_matrix(df_distance, bike_counts, Nc, a, b, c)

        # 只考虑从当前点出发的路径
        nij_sorted = [r for r in nij_sorted if r["from"] == current_location]

        for record in nij_sorted:
            i, j = record["from"], record["to"]
            Nc_new, moved_out, moved_in = perform_dispatch(i, j, Nc, bike_counts, max_capacity)
            print(f"[STEP {step+1}] {i} → {j}, moved_out={moved_out}, moved_in={moved_in}, Nc={Nc_new}, N_i={bike_counts[i]}, N_j={bike_counts[j]}")
            
            Nc = Nc_new
            route.append({
                    "from": i,
                    "N_i": bike_counts[i],
                    "moved_out": moved_out,
                    "to": j,
                    "N_j": bike_counts[j],
                    "moved_in": moved_in,
                    "tij": record["tij"],
                    "Nc": Nc,
                    "step": step + 1
            })
            current_location = j
            break
        else:
            break

    return pd.DataFrame(route)
