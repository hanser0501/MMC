import pandas as pd
import math
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

# 参数设置（a + b + c = 1）
a = 0.6
b = 0.2
c = 0.2

df_distance = pd.read_excel(r"D:\MMC\mmc\data\shortest_matrix.xlsx", index_col=0)
supply_path = r"D:\MMC\mmc\data\supply.xlsx"
demand_path = r"D:\MMC\mmc\data\demand.xlsx"

supply_sheets = pd.read_excel(supply_path, sheet_name=None)
demand_sheets = pd.read_excel(demand_path, sheet_name=None)

writer = pd.ExcelWriter(r"D:\MMC\mmc\data\nij_by_time.xlsx", engine='openpyxl', mode='w')

for time_slot in supply_sheets:
    print(f"处理时间段：{time_slot}")
    df_supply = supply_sheets[time_slot]
    df_demand = demand_sheets.get(time_slot)

    if df_demand is None:
        print(f"[警告] 时间段 {time_slot} 无匹配的需求数据，跳过")
        continue

    if 'location' not in df_supply or 'supply' not in df_supply:
        print(f"[警告] supply sheet '{time_slot}' 缺少必要列")
        continue
    if 'location' not in df_demand or 'demand' not in df_demand:
        print(f"[警告] demand sheet '{time_slot}' 缺少必要列")
        continue

    supply_dict = dict(zip(df_supply['location'], df_supply['supply']))
    demand_dict = dict(zip(df_demand['location'], df_demand['demand']))

    valid_supplies = [min(supply_dict[j], 20) for j in df_supply['location']
                      if j in supply_dict and supply_dict[j] > 0]
    valid_demands = [demand_dict[i] for i in df_demand['location']
                     if i in demand_dict and demand_dict[i] > 0]
    if not valid_supplies or not valid_demands:
        print(f"[跳过] 时间段 {time_slot} 缺少有效供需点")
        continue

    avg_Njf = sum(valid_supplies) / len(valid_supplies)
    avg_Nin = sum(valid_demands) / len(valid_demands)

    nij_list = []
    for j in df_supply['location']:
        for i in df_demand['location']:
            try:
                if supply_dict[j] <= 0 or demand_dict[i] <= 0:
                    continue
                tij = df_distance.loc[j, i] / 416.7  # 单位：米/分钟
                Njf = min(supply_dict[j], 20)
                Nin = demand_dict[i]

                if tij > 0:
                    nij = a / tij + b * Njf / avg_Njf + c * Nin / avg_Nin
                    nij_list.append({
                        'From': j,
                        'To': i,
                        'tij': tij,
                        'Njf': Njf,
                        'Nin': Nin,
                        'nij': nij
                    })
            except KeyError:
                continue

    if nij_list:
        df_nij = pd.DataFrame(nij_list)
        df_nij = df_nij.dropna(subset=['nij'])
        df_nij = df_nij[df_nij['nij'] > 0]
        if not df_nij.empty:
            df_nij.to_excel(writer, sheet_name=time_slot, index=False)
        else:
            print(f"[跳过] 时间段 {time_slot} 所有 nij 无效")
    else:
        print(f"[无结果] 时间段 {time_slot} nij_list 为空")

writer.close()
print("所有时间段的 nij 计算完成，结果已保存。")
