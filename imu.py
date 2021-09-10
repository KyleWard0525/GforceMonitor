"""
Read data from IMU's ICM20948 chip
"""
import time
import machine
import sys
import icm20948
from icm20948 import ICM20948

imu = ICM20948()
imu.icm20948_Gyro_Accel_Read()

gyro_ratio = 32.8
accel_ratio = 16384

gyro = {
    "x": icm20948.Gyro[0]/gyro_ratio,
    "y": icm20948.Gyro[1]/gyro_ratio,
    "z": icm20948.Gyro[2]/gyro_ratio
}

accel = {
    "x": icm20948.Accel[0]/accel_ratio,
    "y": icm20948.Accel[1]/accel_ratio,
    "z": icm20948.Accel[2]/accel_ratio
}

imu.imuAHRSupdate(gyro["x"],gyro["y"],gyro["z"],
                  accel["x"], accel["y"], accel["z"],
                  1,1,1)

print("Gyro X = " + str(gyro["x"]) + " deg/sec")
print("Gyro Y = " + str(gyro["y"]) + " deg/sec")
print("Gyro Z = " + str(gyro["z"]) + " deg/sec")
print("\n")
print("Accel X = " + str(accel["x"]) + " g")


                  
                 