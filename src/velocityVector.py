import cv2
import numpy as np
import math
from time import sleep
from i2c_comms import I2CComms

angle35 = np.radians(35)  # Convert degrees to radians
angle1175 = np.radians(117.5)
YPM = 100/480 * np.sin(angle35)/np.sin(angle1175) # Replace with your desired constant
Y_PIXEL_TO_MM = np.array([(i * YPM * np.sin(angle1175)/np.sin(angle35)) for i in range(480)])
# print(Y_PIXEL_TO_MM)

X_PIXEL_TO_MM = 10  # Replace with your desired constant


def get_trajectory_vector(image):
    """
    Processes the given image, detects the red path, and calculates a trajectory vector.

    :param image: The input frame from the robot's camera
    :return: (dx, dy) trajectory vector in image coordinates
    """
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the HSV range for detecting red color
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    # Define the HSV range for detecting blue color
    # lower_blue1 = np.array([100, 150, 50])
    # upper_blue1 = np.array([120, 255, 255])
    # lower_blue2 = np.array([120, 150, 50])
    # upper_blue2 = np.array([140, 255, 255])

    # Create masks for the red color range
    mask_r1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_r2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_r1, mask_r2)
    
    # mask_b1 = cv2.inRange(hsv, lower_blue1, upper_blue1)
    # mask_b2 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    # mask_blue = cv2.bitwise_or(mask_b1, mask_b2)

    # Apply morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
    
    # Apply morphological operations to clean up the mask
    # kernel = np.ones((5, 5), np.uint8)
    # mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel)
    # mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)

    # Find contours in the mask
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find contours in the mask
    # contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # if contours_blue:
    #     return True
    if contours_red:
        # Find the largest contour (assumed to be the red path)
        largest_contour = max(contours_red, key=cv2.contourArea)

        # Calculate the center of the largest contour
        moments = cv2.moments(largest_contour)
        if moments['m00'] > 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])

            # Get the bottom center of the frame (robot's perspective origin)
            height, width, _ = image.shape
            bottom_center = (width // 4, height)

            # Calculate trajectory vector (dx, dy)
            dx = cx - bottom_center[0]  # Horizontal offset (strafe direction)
            dy = bottom_center[1] - cy  # Vertical distance to the path end

            # Calculate the angle relative to the forward direction (0 degrees)
            angle = math.degrees(math.atan2(dx, dy))
            angle = math.floor(angle)

            # Visualize the path and trajectory vector on the frame
            # cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)  # Path center
            # cv2.line(image, bottom_center, (cx, cy), (255, 0, 0), 2)  # Trajectory vector
            # cv2.drawContours(image, [largest_contour], -1, (0, 255, 255), 2)  # Path contour

            return dx, dy, angle

    return None  # Return None if no path is detected

# Main loop for processing video feed
def main():
    # Open the camera feed
    cap = cv2.VideoCapture(0)  # Change to the appropriate camera index if needed
    i2c = I2CComms(1, 0x08)
    
    # i2c.write_block(0x05, [True], '=?') #ready to start
    
    # while True:
    #     resume = i2c.read_block(0x06, 1)
    #     if resume:
    #         break
    #     sleep(0.01)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame for faster processing (optional)
        frame = cv2.resize(frame, (640, 480))

        # Get trajectory vector
        trajectory = get_trajectory_vector(frame)

        # if trajectory == True:
        #     print("Arrived ")
        #     i2c.write_block(0x01, [True], '=?')
        #     while True:
        #         resume = i2c.read_block(0x01, 1)
        #         if resume:
        #             break
        #         sleep(0.01)
        if trajectory:
            dx, dy, angle = trajectory
            dx = dx*X_PIXEL_TO_MM
            dy = Y_PIXEL_TO_MM[dy]
            
            print(f"Trajectory Vector: dx={dx}, dy={dy}, angle={angle} degrees")
            
            i2c.write_block(0x00, [dx, dy, angle], '=fff')            
        else:
            print(f"No path detected: dx={0}, dy={0}, angle={0} degrees")
            i2c.write_block(0x02, [0, 0, 0], '=hhh')

        # Show the processed frame
        # cv2.imshow('Frame', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        sleep(0.01)

    cap.release()
    # cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
