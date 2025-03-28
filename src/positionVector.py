import json
import struct
import cv2
import numpy as np
import math
import keyboard
from time import sleep
from i2c_comms import I2CComms

State = dict(
    Disabled = int(0),
    Enabled = int(1),
    Enabling_Transition = int(2),
    Disabling_Transition = int(3),
    Pickup_Transition = int(4),
    Dropoff_Transistion = int(5)
)
    
Event = dict(
    No_Event = int(0),
    Enable = int(1),
    Disable = int(2),
    Pickup = int(3),
    Dropoff = int(4)
)

# Main loop for processing video feed
def main():
    # Open the camera feed
    # cap = cv2.VideoCapture(0)  # Change to the appropriate camera index if needed
    i2c = I2CComms(1, 0x08)
    
    direction = True
    destination_X = 0
    destination_Y = 0
    looktowards_Angle = 0
    
    i2c.write_block(0x05, [Event['Enable']], "=B") #ready to start
    # input("potato:")
    while True:
        result = i2c.read_block(0x85, 1)
        if result[0] == State['Enabled']:
            break
        sleep(0.01)

    while True:
        state = i2c.read_block(0x85, 1)
        
        sleep(0.01)
        
        if state[0] == State['Disabled']:
            print(f"Disabled")
            break
        if state[0] != State['Enabled']:
            print(f"Not Enabled")
            continue
        
        
        if keyboard.is_pressed('w'):
            destination_Y += 0.001
        if keyboard.is_pressed('a'):
            destination_X -= 0.001
        if keyboard.is_pressed('s'):
            destination_Y -= 0.001
        if keyboard.is_pressed('d'):
            destination_X += 0.001
        if keyboard.is_pressed('q'):
            direction = False
        elif keyboard.is_pressed('e'):
            direction = True
        else:
            direction = None
            
        if keyboard.is_pressed('g'):
            i2c.write_block(0x05, [Event['Disable']], "=B") #ready to start
            break
        
        if direction == None:
            i2c.write_block(0x10, [destination_X, destination_Y, looktowards_Angle], '=fff')
        elif direction != None:
            i2c.write_block(0x02, [direction], '=B')

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    
    

if __name__ == "__main__":
    main()
