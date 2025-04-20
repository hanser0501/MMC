# MMC
说明：
- 代码主要用于对第17届华中杯数模挑战赛的B题-任务2进行调度模型建立和求解
- 基于 Python 3.12开发，依赖库： pandas, numpy, matplotlib, networkx
- 主程序：dispatch_multi.py
- 使用方法：
    1. 在calc_shortest中生成站点距离矩阵文件 shortest_matrix.xlsx
    2. 准备初始站点单车需求量或可供给量 points_number.xlsx
    3. 修改distance_file和count_file为你的矩阵文件和站点数量文件路径（建议使用绝对路径）
    4. 修改result_path为你需要的调度路线文件输出路径
- 实现功能：
    1. 输出含有车辆标号、出发点与到达点以及装载量等数据的调度路线文件
    2. 生成直观的调度车运行路线

- 重要程序：calc_shortest
- 使用方法：
    1. 准备站点坐标文件 points.xlsx
    2. 准备站点邻近文件 edges.xlsx （所有相邻站点对）
    3. 修改points_path和edges_path为你的文件路径
- 实现功能：
    1. 输出任意两站点之间的最短路线距离文件
    2. 生成直观的路线图及距离参数
    3. 生成热力图（可选）

- 代码附加功能说明：
- 可以在终端使用pip install -r requirements/dev.txt来下载所有依赖库