from time import sleep
from smbus2 import SMBus
import struct

class I2CComms:
    def __init__(self, bus_num, device_addr):
        self.bus_num = bus_num
        self.device_addr = device_addr
        while True:
            try:
                self.bus = SMBus(bus_num)
                break
            except Exception as e:
                print(f"Error: {e}")
                pass

    def write_byte(self, value):
        self.bus.write_byte(self.device_addr, value)

    def read_byte(self):
        return self.bus.read_byte(self.device_addr)

    def write_block(self, data, format_string):
        try:
            struc = list(struct.pack(format_string, *data))
            length_of_data = len(struc)
            self.bus.write_i2c_block_data(self.device_addr, length_of_data, struc)
            print(f"Send Data: {data} of Length: {length_of_data}")
        except Exception as e:
            print(f"Error: {e}")


    def read_block(self, register, number_of_values):
        return self.bus.read_i2c_block_data(self.device_addr, register, number_of_values)

    def close(self):
        self.bus.close()

    def test(self):
        for x in range(1,5):
            self.write_block(5, [1,2,3,4,5])


i2c = I2CComms(1, 0x08)

i2c.write_block([0x05], "=B")
sleep(5)
i2c.write_block([0x06], "=B")

while True:
    dx = 1.1
    dy = 2.1
    angle = 90.1

    # dx = math.floor(np.interp(dx, [-320, 320], [0,255]))
    # dy = math.floor(np.interp(dy, [0, 480], [0,255]))
    # angle = math.floor(np.interp(angle, [0, 360], [0,255]))
    
    # print(f"Trajectory Vector: dx={dx}, dy={dy}, angle={angle} degrees")
    
    # val = i2c.read_byte(1)
    # print(f"Byte: {val}")
    sleep(1)
    