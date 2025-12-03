from mpu6050 import mpu6050

class MPU6050:
    def __init__(self, address=0x68):
        self.sensor = mpu6050(address)

    def read(self):
        accel = self.sensor.get_accel_data()
        gyro  = self.sensor.get_gyro_data()
        temp  = self.sensor.get_temp()

        return {
            "accel_x": accel["x"],
            "accel_y": accel["y"],
            "accel_z": accel["z"],
            "gyro_x": gyro["x"],
            "gyro_y": gyro["y"],
            "gyro_z": gyro["z"],
            "temp_c": temp,
        }