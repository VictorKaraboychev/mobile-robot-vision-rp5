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


input("enter to continue")
i2c.write_block(0x05, [Event["Loading"]], '=B')