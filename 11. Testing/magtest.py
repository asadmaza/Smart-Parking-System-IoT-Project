# Kexin's Code for real car detection using magnetometer
from PiicoDev_QMC6310 import PiicoDev_QMC6310
from PiicoDev_Unified import sleep_ms

# 初始化传感器
magSensor = PiicoDev_QMC6310(range=3000)

while True:
    raw_data = magSensor.read() # 读取每个轴上的场强（uT）
    
    z_axis_strength = raw_data['z']  # 获取Z轴的数据
    print(f"Z Axis: {z_axis_strength} uT")  # 打印Z轴的数据
    
    sleep_ms(1000)