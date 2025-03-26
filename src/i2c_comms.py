import math
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
        try:
            return self.bus.read_byte(self.device_addr)
        except Exception as e:
            print(f"Error: {e}")

    def write_block(self, cmd, data = [], format_string = '='):
        try:
            struc = list(struct.pack(format_string, *data))
            length = list(struct.pack("=B", len(struc)))
            data_to_send = length + struc
            self.bus.write_i2c_block_data(self.device_addr, cmd, data_to_send)
            # print(f"Send Data: {data_to_send} to: {cmd}")
        except Exception as e:
            print(f"Error: {e}")


    def read_block(self, register, number_of_values):
        try:
            retval = self.bus.read_i2c_block_data(self.device_addr, register, number_of_values)
            print(f"Recieved Data: {retval} to: {register}")
            return retval
        except Exception as e:
            print(f"Error: {e}")

    def close(self):
        self.bus.close()

    def test(self):
        for x in range(1,5):
            self.write_block(5, [1,2,3,4,5])


i2c = I2CComms(1, 0x08)
i2c.write_block(0x05, [1], "=?") #ready to start
input("Press Enter to continue...")
i2c.write_block(0x10, [-0.018, -0.1225, 0], '=fff')

# # i2c.write_block([0x69, True, 4.20], "=B?f")
# input("Press Enter to continue...")
# i2c.write_block(0x05, [True], "=?") #ready to start

# while True:
#     result = i2c.read_block(0x85, 1)
#     if result[0]:
#         break
#     sleep(0.01)

# input("Press Enter to continue...")
# i2c.write_block(0x11) #ready to start

# while True:
#     result = i2c.read_block(0x86, 1)
#     if result[0]:
#         break
#     sleep(0.01)
    
# input("Press Enter to continue...")
# i2c.write_block(0x12) #ready to start

# input("Press Enter to continue...")
# i2c.write_block(0x05, [False], "=?") #ready to start

# while True:
#     result = i2c.read_block(0x85, 1)
#     if not result[0]:
#         break
#     sleep(0.01)

# while True:
#     dx = 1.1
#     dy = 2.1
#     angle = 90.1

#     # dx = math.floor(np.interp(dx, [-320, 320], [0,255]))
#     # dy = math.floor(np.interp(dy, [0, 480], [0,255]))
#     # angle = math.floor(np.interp(angle, [0, 360], [0,255]))
    
#     # print(f"Trajectory Vector: dx={dx}, dy={dy}, angle={angle} degrees")
    

#     # val = i2c.read_block(0x81, 12)
#     # print(f"Byte: {val}")
#     sleep(1)
    
    
# with open("sensor_data.txt", "a") as file:
#     while True:
#         val = i2c.read_block(0x81, 12)
        
#         data = struct.unpack("=fff", bytes(val))
        
#         file.write(val+ "\n")
#         file.flush()
        
#         print(data)
        
#         sleep(0.5)