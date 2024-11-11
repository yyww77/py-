import pandapower as pp
import pandapower.shortcircuit as sc
import pandapower.plotting as plot
import warnings
import pandas as pd
import numpy as np
warnings.simplefilter(action='ignore', category=FutureWarning)

# 定义最大和最小模式的电流
Imax = 6.72  # 最大电流，单位：kA
Imin = 3.35  # 最小电流，单位：kA
s_sc_mva_max = 35 * Imax * np.sqrt(3)
s_sc_mva_min = 35 * Imin * np.sqrt(3)

# 创建网络
def create_network():
    net = pp.create_empty_network()
    return net

# 添加母线、外部电网、变压器、线路和负荷
def add_elements(net):

    # 添加母线
    bus35kv_main = pp.create_bus(net, vn_kv=35, name="35kV Main Bus")
    bus35kv_sec = pp.create_bus(net, vn_kv=35, name="35kV Sectionalized Bus")
    bus6kv_1 = pp.create_bus(net, vn_kv=6.3, name="6.3kV Bus 1")
    bus6kv_2 = pp.create_bus(net, vn_kv=6.3, name="6.3kV Bus 2")
    bus6kv_3 = pp.create_bus(net, vn_kv=6, name="6kV Load 1")
    bus6kv_4 = pp.create_bus(net, vn_kv=6, name="6kV Load 2")

    # 添加母线分段断路器
    pp.create_switch(net, bus35kv_main, bus35kv_sec, et="b", closed=False, name="Bus Coupler")

    # 外部电网
    ext_grid1 = pp.create_ext_grid(net, bus=bus35kv_main, vm_pu=1.02, s_sc_max_mva=s_sc_mva_max,
                                   s_sc_min_mva=s_sc_mva_min, rx_max=0.23229, rx_min=0.46498)
    ext_grid2 = pp.create_ext_grid(net, bus=bus35kv_sec, vm_pu=1.02, s_sc_max_mva=s_sc_mva_max,
                                   s_sc_min_mva=s_sc_mva_min, rx_max=0.23229, rx_min=0.46498)

    # 为外部电源指定零序阻抗和负序阻抗的最大和最小值
    for ext_grid in [ext_grid1, ext_grid2]:
        net.ext_grid.loc[ext_grid, 'x0x_max'] = 0.1
        net.ext_grid.loc[ext_grid, 'x0x_min'] = 0.05
        net.ext_grid.loc[ext_grid, 'r0x0_max'] = 0.1
        net.ext_grid.loc[ext_grid, 'r0x0_min'] = 0.05

    # 添加变压器
    # 添加变压器 1
    pp.create_transformer_from_parameters(
        net, hv_bus=bus35kv_main, lv_bus=bus6kv_1, sn_mva=25, vn_hv_kv=35, vn_lv_kv=6.3,
        vk_percent=8.16, vkr_percent=0.5, pfe_kw=50, i0_percent=0.1, shift_degree=0,
        vector_group="Dyn", name="Transformer 1",
        vk0_percent=8.16, vkr0_percent=0.5, mag0_percent=100, mag0_rx=0, si0_hv_partial=0.9
    )

    # 添加变压器 2
    pp.create_transformer_from_parameters(
        net, hv_bus=bus35kv_sec, lv_bus=bus6kv_2, sn_mva=25, vn_hv_kv=35, vn_lv_kv=6.3,
        vk_percent=7.88, vkr_percent=0.5, pfe_kw=50, i0_percent=0.1, shift_degree=0,
        vector_group="Dyn", name="Transformer 2",
        vk0_percent=7.88, vkr0_percent=0.5, mag0_percent=100, mag0_rx=0, si0_hv_partial=0.9
    )

    # 添加线路
    line_parameters = [
        (bus6kv_1, bus6kv_3, 375, 0.0182, 0.03, "6102&1#加氢线"),
        (bus6kv_1, bus6kv_3, 700, 0.0341, 0.056, "6103&1#循环水线"),
        (bus6kv_1, bus6kv_3, 23, 0.0044, 0.0018, "6104&1#消弧线圈"),
        (bus6kv_1, bus6kv_3, 428, 0.0321, 0.0342, "6105&1#压缩机"),
        (bus6kv_1, bus6kv_3, 445, 0.0216, 0.0356, "6106&1#常减压"),
        (bus6kv_1, bus6kv_3, 401, 0.0195, 0.0321, "6107&1#裂化线"),
        (bus6kv_1, bus6kv_3, 302, 0.0147, 0.0242, " 6108&1#制氢"),
        (bus6kv_1, bus6kv_3, 32, 0.0061, 0.0026, " 6109&1#电容器"),
        (bus6kv_1, bus6kv_3, 1028, 0.05, 0.0822, "6113&1#焦化线"),
        (bus6kv_1, bus6kv_3, 1160, 0.0564, 0.0928, " 6114&1#泡沫站线"),
        (bus6kv_2, bus6kv_4, 391, 0.019, 0.0313, " 6202&2#加氢线"),
        (bus6kv_2, bus6kv_4, 612, 0.0298, 0.049, " 6203&2#循环水线"),
        (bus6kv_2, bus6kv_4, 430, 0.0323, 0.0344, " 6204&2#压缩机"),
        (bus6kv_2, bus6kv_4, 438, 0.0329, 0.035, " 6205&3#压缩机"),
        (bus6kv_2, bus6kv_4, 432, 0.021, 0.0346, " 6206&2#常减压"),
        (bus6kv_2, bus6kv_4, 396, 0.0193, 0.0317, "6207&2#裂化线"),
        (bus6kv_2, bus6kv_4, 321, 0.0156, 0.0257, " 6208&2#制氢线"),
        (bus6kv_2, bus6kv_4, 21, 0.004, 0.0017, " 6209&2#电容器"),
        (bus6kv_2, bus6kv_4, 44, 0.0083, 0.0035, "6212&2#消弧线圈"),
        (bus6kv_2, bus6kv_4, 1027, 0.05, 0.0822, " 6213&2#焦化线"),
        (bus6kv_2, bus6kv_4, 1164, 0.0566, 0.0931, "62142&#泡沫站线"),
    ]

    for from_bus, to_bus, length, r, x, name in line_parameters:
        pp.create_line_from_parameters(net, from_bus=from_bus, to_bus=to_bus, length_km=length/1000,
                                       r_ohm_per_km=r, x_ohm_per_km=x, c_nf_per_km=0, max_i_ka=1,
                                       r0_ohm_per_km=r, x0_ohm_per_km=x, c0_nf_per_km=0, name=name, endtemp_degree=80)

     # 添加负荷
    for i in range(13):
        pp.create_load(net, bus=bus6kv_3, p_mw=0.6, q_mvar=0.2, name=f"Load {i + 1} on Bus 6kV-3")
        pp.create_load(net, bus=bus6kv_4, p_mw=0.6, q_mvar=0.2, name=f"Load {i + 14} on Bus 6kV-4")

def calculate_protection_setpoints(data_frame, device_type, K_values, Imax_1ph=None, Imin_1ph=None):
    """
    计算保护定值：速断保护、限时电流速断保护、定时限过流保护
    """
    setpoints = data_frame.copy()
    fault_types = ['3ph', '2ph', '1ph']
    for fault_type in fault_types:
        column_name = f'{fault_type}_ikss_ka'
        if column_name not in setpoints.columns:
            continue
        base_current = setpoints[column_name] * 1000  # 转换为安培
        for protection_type in ['instantaneous', 'time_delayed', 'time_graded']:
            k_value = K_values.get((fault_type, protection_type), 1.2)
            setpoint_name = f'setpoint_{fault_type}_{protection_type}'
            setpoints[setpoint_name] = k_value * base_current
            if protection_type == 'time_delayed':
                setpoints[f'time_delayed_{fault_type}'] = 0.1  # 时间延迟，单位秒
            elif protection_type == 'time_graded':
                setpoints[f'time_graded_{fault_type}'] = 0.2  # 时间延迟，单位秒
    # 根据不同设备类型添加特定逻辑
    if device_type == 'transformer':
        setpoints = calculate_transformer_specific_setpoints(setpoints, K_values)
    elif device_type == 'line_end':
        setpoints = calculate_line_end_specific_setpoints(setpoints, K_values)
    return setpoints

def calculate_transformer_specific_setpoints(setpoints, K_values):
    fault_type = '3ph'
    k_value = K_values.get((fault_type, 'instantaneous'), 1.2)
    # 确保列名与实际存在的列名匹配
    setpoints[f'setpoint_hv_{fault_type}_inst'] = k_value * setpoints.get(f'hv_bus_{fault_type}_ikss_ka', 0) * 1000
    setpoints[f'setpoint_lv_{fault_type}_inst'] = k_value * setpoints.get(f'lv_bus_{fault_type}_ikss_ka', 0) * 1000
    return setpoints

def calculate_line_end_specific_setpoints(setpoints, K_values):
    fault_type = '3ph'
    k_value = K_values.get((fault_type, 'instantaneous'), 1.2)
    # 确保列名与实际存在的列名匹配
    setpoints[f'setpoint_from_{fault_type}_inst'] = k_value * setpoints.get(f'from_bus_{fault_type}_ikss_ka', 0) * 1000
    setpoints[f'setpoint_to_{fault_type}_inst'] = k_value * setpoints.get(f'to_bus_{fault_type}_ikss_ka', 0) * 1000
    return setpoints

# 使用新的函数计算保护定值
def run_short_circuit_and_set_protection(net, case='max', lv_tol_percent=6):
    sc_results, line_end_short_circuit_df, transformer_short_circuit_df, bus_short_circuit_df = run_short_circuit_calculation(
        net, case, lv_tol_percent)

    # 确保 K_values 是一个字典
    K_values = {
        ('3ph', 'instantaneous'): 1.2,
        ('3ph', 'time_delayed'): 1.8,
        ('3ph', 'time_graded'): 2.4,
        ('2ph', 'instantaneous'): 1.1,
        ('2ph', 'time_delayed'): 1.7,
        ('2ph', 'time_graded'): 2.3,
        ('1ph', 'instantaneous'): 1.0,
        ('1ph', 'time_delayed'): 1.6,
        ('1ph', 'time_graded'): 2.2
    }
    protection_setpoints = calculate_protection_setpoints(sc_results, 'some_device_type', K_values, Imax, Imin)
    transformer_setpoints = calculate_transformer_setpoints(transformer_short_circuit_df, K_values)
    line_end_setpoints = calculate_line_end_setpoints(line_end_short_circuit_df, K_values)
    return protection_setpoints, transformer_setpoints, line_end_setpoints, line_end_short_circuit_df, transformer_short_circuit_df, bus_short_circuit_df

# 定义变压器保护定值计算函数
def calculate_transformer_setpoints(transformer_short_circuit_df, K_values):
    transformer_setpoints = transformer_short_circuit_df.copy()
    fault_type = '3ph'
    for protection_type in ['instantaneous']:
        k_value = K_values.get((fault_type, protection_type), 1.2)
        transformer_setpoints[f'setpoint_hv_{fault_type}_{protection_type}'] = k_value * transformer_setpoints[f'hv_bus_{fault_type}_ikss_ka'] * 1000
        transformer_setpoints[f'setpoint_lv_{fault_type}_{protection_type}'] = k_value * transformer_setpoints[f'lv_bus_{fault_type}_ikss_ka'] * 1000
    return transformer_setpoints

# 定义线路末端保护定值计算函数
def calculate_line_end_setpoints(line_end_short_circuit_df, K_values):
    line_end_setpoints = line_end_short_circuit_df.copy()
    fault_type = '3ph'
    for protection_type in ['instantaneous']:
        k_value = K_values.get((fault_type, protection_type), 1.2)
        line_end_setpoints[f'setpoint_from_{fault_type}_{protection_type}'] = k_value * line_end_setpoints[f'from_bus_{fault_type}_ikss_ka'] * 1000
        line_end_setpoints[f'setpoint_to_{fault_type}_{protection_type}'] = k_value * line_end_setpoints[f'to_bus_{fault_type}_ikss_ka'] * 1000
    return line_end_setpoints

# 定义计算短路电流的函数
def run_short_circuit_calculation(net, case='max', lv_tol_percent=6):
    # 清空之前的短路计算结果
    net.res_bus_sc.drop(index=net.res_bus_sc.index, inplace=True)

    # 执行短路计算
    sc.calc_sc(net, fault="3ph", case=case, lv_tol_percent=lv_tol_percent)
    sc.calc_sc(net, fault="2ph", case=case, lv_tol_percent=lv_tol_percent)
    sc.calc_sc(net, fault="1ph", case=case, lv_tol_percent=lv_tol_percent)

    # 获取短路计算结果
    sc_results = net.res_bus_sc.copy()

    # 线路两端短路电流
    line_end_short_circuit = []
    for line in net.line.index:
        from_bus = net.line.at[line, 'from_bus']
        to_bus = net.line.at[line, 'to_bus']
        from_bus_sc = sc_results.at[from_bus, 'ikss_ka'] if not sc_results.empty else 0
        to_bus_sc = sc_results.at[to_bus, 'ikss_ka'] if not sc_results.empty else 0
        line_end_short_circuit.append({
            "line_name": net.line.at[line, 'name'],
            "from_bus_3ph_ikss_ka": from_bus_sc,
            "to_bus_3ph_ikss_ka": to_bus_sc
        })

    line_end_short_circuit_df = pd.DataFrame(line_end_short_circuit)

    # 变压器高压和低压侧短路电流
    transformer_short_circuit = []
    for trafo in net.trafo.index:
        hv_bus = net.trafo.at[trafo, 'hv_bus']
        lv_bus = net.trafo.at[trafo, 'lv_bus']
        hv_bus_sc = sc_results.at[hv_bus, 'ikss_ka'] if not sc_results.empty else 0
        lv_bus_sc = sc_results.at[lv_bus, 'ikss_ka'] if not sc_results.empty else 0
        transformer_short_circuit.append({
            "transformer_name": net.trafo.at[trafo, 'name'],
            "hv_bus_3ph_ikss_ka": hv_bus_sc,
            "lv_bus_3ph_ikss_ka": lv_bus_sc
        })

    transformer_short_circuit_df = pd.DataFrame(transformer_short_circuit)

    return sc_results, line_end_short_circuit_df, transformer_short_circuit_df

def plot_network(net):
    plot.simple_plot(net)


def main():
    net = create_network()
    add_elements(net)

    try:
        # 最大模式短路计算
        sc_results_max, line_sc_max, trafo_sc_max = run_short_circuit_calculation(net, case='max')

        # 最小模式短路计算
        sc_results_min, line_sc_min, trafo_sc_min = run_short_circuit_calculation(net, case='min')

        # 将结果保存到Excel
        with pd.ExcelWriter("short_circuit_results.xlsx") as writer:
            sc_results_max.to_excel(writer, sheet_name='Max Mode Bus', index=False)
            line_sc_max.to_excel(writer, sheet_name='Max Mode Line Ends', index=False)
            trafo_sc_max.to_excel(writer, sheet_name='Max Mode Transformer', index=False)
            sc_results_min.to_excel(writer, sheet_name='Min Mode Bus', index=False)
            line_sc_min.to_excel(writer, sheet_name='Min Mode Line Ends', index=False)
            trafo_sc_min.to_excel(writer, sheet_name='Min Mode Transformer', index=False)

        print("短路计算结果已保存到 short_circuit_results.xlsx")

    except Exception as e:
        print(f"运行短路计算时出现错误: {e}")

    # 绘制网络拓扑图
    plot_network(net)

if __name__ == "__main__":
    main()
