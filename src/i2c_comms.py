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

    def write_block(self, register, data, format_string):
        try:
            struc = struct.pack(format_string, *data)
            self.bus.write_i2c_block_data(self.device_addr, register, list(struc))
        except Exception as e:
            print(f"Error: {e}")


    def read_block(self, register):
        return self.bus.read_i2c_block_data(self.device_addr)

    def close(self):
        self.bus.close()

    def test(self):
        for x in range(1,5):
            self.write_block(5, [1,2,3,4,5])
