from i2c_comms import I2CComms


i2c = I2CComms(1, 0x08)

Event = dict(
    No_Event = int(0),
    Enable = int(1),
    Disable = int(2),
    Pickup = int(3),
    Dropoff = int(4),
    Loading = int(5)
)

while(True):
    
    option = input("Pick: loading, enable, disable, pickup, dropoff ----- ")

    if option == "loading":
        i2c.write_block(0x05, [Event["Loading"]], '=B')
    elif option == "enable":
        i2c.write_block(0x05, [Event["Enable"]], '=B')
    elif option == "disable":
        i2c.write_block(0x05, [Event["Disable"]], '=B')
    elif option == "pickup":
        i2c.write_block(0x05, [Event["Pickup"]], '=B')
    elif option == "dropoff":
        i2c.write_block(0x05, [Event["Dropoff"]], '=B')
    else:
        break
