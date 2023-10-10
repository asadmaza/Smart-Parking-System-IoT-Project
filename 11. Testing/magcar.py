# Kexin's Code for real car detection using magnetometer
from PiicoDev_QMC6310 import PiicoDev_QMC6310
from PiicoDev_Unified import sleep_ms

# 初始化传感器
magSensor = PiicoDev_QMC6310(range=3000)

def get_average(data_list):
    return sum(data_list) / len(data_list)

def collect_data_for_seconds(seconds):
    data_list = []
    for _ in range(seconds):
        raw_data = magSensor.read()
        z_axis_strength = raw_data['z']
        data_list.append(z_axis_strength)
        sleep_ms(1000)
    return data_list

# 循环直到获取一个有效的默认值
while True:
    # 读取前十秒的数据
    data_list = collect_data_for_seconds(10)
    
    # 如果数据波动小于2%，将其设为默认值
    avg_value = get_average(data_list)
    max_value = max(data_list)
    min_value = min(data_list)
    fluctuation = (max_value - min_value) / avg_value
    
    if fluctuation < 0.02:
        default_value = avg_value
        break

# 主循环
try:
    while True:
        raw_data = magSensor.read()
        z_axis_strength = raw_data['z']

        if abs((z_axis_strength - default_value) / default_value) > 0.10:
            print("detected car")
        else:
            print("no car")
        
        sleep_ms(1000)
except KeyboardInterrupt:
    print("\nProgram terminated.")