import json
import struct
import cv2
import numpy as np
import math
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

PickedUp = False

# Camera intrinsic parameters
focal_length_mm = 4.0
diagonal_fov_deg = 55.0
image_width = 640
image_height = 480

# Calculate focal length in pixels
diagonal_pixels = np.sqrt(image_width**2 + image_height**2)
fov_rad = np.radians(diagonal_fov_deg)
focal_length_px = diagonal_pixels / (2 * np.tan(fov_rad / 2))

# Assume square pixels, so fx = fy
fx = focal_length_px
fy = focal_length_px
cx = image_width / 2
cy = image_height / 2
K = np.array([[fx, 0, cx],
            [0, fy, cy],
            [0, 0, 1]], dtype=np.float32)

# Extrinsic parameters
tilt_angle_deg = -30  # Tilt from horizontal
height = 0.1025  # 5 cm in meters

# Rotation matrix (tilt around X-axis)
theta = np.radians(tilt_angle_deg)
cos_theta = np.cos(theta)
sin_theta = np.sin(theta)
R = np.array([[1, 0, 0],
            [0, cos_theta, -sin_theta],
            [0, sin_theta, cos_theta]], dtype=np.float32)

# Camera position in world coordinates (ground at Z=0)
C = np.array([0, 0, height], dtype=np.float32)
t = R @ -C  # Translation vector

# Homography matrix H = K * [R1 R2 t]
R1 = R[:, 0]
R2 = R[:, 1]
H_columns = np.column_stack((-R1, R2, t))
H = K @ H_columns

# Inverse homography to map image to ground
H_inv = np.linalg.inv(H)

def find_real_world_coordinates(x, y):
    pixel = np.array([[[x, y]]], dtype=np.float32)
    ground_point = cv2.perspectiveTransform(pixel, H_inv)
    return ground_point[0][0][:2]  # Return X, Y (Z=0)

REF = find_real_world_coordinates(image_width // 2 , image_height)

def get_trajectory_vector(image):
    """
    Processes the given image, detects the red path, and calculates a trajectory vector.

    :param image: The input frame from the robot's camera
    :return: (dx, dy) trajectory vector in image coordinates
    """
    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the HSV range for detecting red color
    lower_red1 = np.array([0, 130, 130])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # Define the HSV range for detecting blue color
    # lower_blue1 = np.array([120, 50, 20])
    # upper_blue1 = np.array([255, 50, 80])
    
    lower_blue1 = np.array([100, 150, 50])
    upper_blue1 = np.array([130, 255, 255])
    

    # Create masks for the red color range
    mask_r1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_r2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = cv2.bitwise_or(mask_r1, mask_r2)
    
    mask_blue = cv2.inRange(hsv, lower_blue1, upper_blue1)

    # Apply morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
    
    blue_count = cv2.countNonZero(mask_blue)
    
    # # Apply morphological operations to clean up the mask
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel)
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, kernel)

    # Find contours in the mask
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find contours in the mask
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if blue_count > image_height*image_width*0.10:
        print(blue_count)
        # sleep(10000)
        # Find the largest contour (assumed to be the red path)
        largest_contour = max(contours_blue, key=cv2.contourArea)

        # Calculate trajectory vector (dx, dy)
        cx = 0
        cy = 0
        # Calculate the center of the largest contour
        moments = cv2.moments(largest_contour)
        if moments['m00'] > 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
            
            # Visualize the path and trajectory vector on the frame
        return True, cx, cy
    if contours_red:
        # Find the largest contour (assumed to be the red path)
        largest_contour = max(contours_red, key=cv2.contourArea)

        # Calculate trajectory vector (dx, dy)
        cx = 0
        cy = 0
        # Calculate the center of the largest contour
        moments = cv2.moments(largest_contour)
        if moments['m00'] > 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])

            # Get the bottom center of the frame (robot's perspective origin)
            height, width, _ = image.shape
            bottom_center = (width // 2, height)
            
            # Visualize the path and trajectory vector on the frame
            
        # cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)  # Path center
        # cv2.line(image, bottom_center, (cx, cy), (255, 0, 0), 2)  # Trajectory vector
        # cv2.drawContours(image, [largest_contour], -1, (0, 255, 255), 2)  # Path contour
        
        # return dx, dy

        # Get the bottom center of the frame (robot's perspective origin)
        height, width, _ = image.shape
        bottom_center = (width // 2, height)
        bc_x, bc_y = bottom_center

        # Reshape contour points to a 2D array of (x, y) coordinates
        contour_points = largest_contour.reshape(-1, 2)
        
        if contour_points.size == 0:
            return None  # No points in the contour

        # Calculate squared distances from bottom_center to all contour points
        distances_sq = (contour_points[:, 0] - bc_x)**2 + (contour_points[:, 1] - bc_y)**2
        farthest_idx = np.argmax(distances_sq)
        fx, fy = contour_points[farthest_idx]

        # # Visualize the path and trajectory vector on the frame
        # cv2.circle(image, (fx, fy), 5, (0, 255, 0), -1)  # Path center
        # cv2.line(image, (cx,cy), (fx, fy), (0, 255, 0), 2)  # Trajectory vector
        # cv2.drawContours(image, [largest_contour], -1, (0, 255, 255), 2)  # Path contour

        return False, cx, cy, fx, fy

    return None  # Return None if no path is detected

# Main loop for processing video feed
def main():
    # Open the camera feed
    cap = cv2.VideoCapture(0)  # Change to the appropriate camera index if needed
    i2c = I2CComms(1, 0x08)
    
    direction = True
    
    i2c.write_block(0x05, [Event['Enable']], "=B") #ready to start
    # input("potato:")
    while True:
        result = i2c.read_block(0x85, 1)
        if result[0] == State['Enabled']:
            break
        sleep(0.01)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame for faster processing (optional)
        frame = cv2.resize(frame, (640, 480))

        # Get trajectory vector
        trajectory = get_trajectory_vector(frame)
        
        state = i2c.read_block(0x85, 1)
        
        sleep(0.01)
        
        if state[0] == State['Disabled']:
            print(f"Disabled")
            break
        if state[0] != State['Enabled']:
            print(f"Not Enabled")
        elif trajectory == None:
            print(f"No path detected")
            # dy = 0
            # dx = 0
            # if direction:
            #     angle = 0
            # else:
            #     angle = math.pi/2

            # i2c.write_block(0x10, [0, 0, math.pi/2], '=fff')
            i2c.write_block(0x02, [direction], '=B')
        elif trajectory[0] == True:
            print("Arrived ")
            cx = trajectory[1]
            cy = trajectory[2]
            cp = find_real_world_coordinates(cx, cy)
            dist_x, dist_y = cp - REF
            # input("enter to continue")
            print(f"Trajectory Vector: dx={dist_x} m, dy={dist_y} m")
            i2c.write_block(0x05, [Event['Pickup'], dist_x, dist_y], '=Bff')
            # sleep(15)
        elif trajectory[0] == False:
            cx = trajectory[1]
            cy = trajectory[2]
            fx = trajectory[3]
            fy = trajectory[4]

            cp = find_real_world_coordinates(cx, cy)
            fp = find_real_world_coordinates(fx, fy)

            dist_x, dist_y = cp - REF
            look_x, look_y = fp - cp
            look_angle = math.atan2(look_y, look_x)
            
            if look_x - dist_x > 0:
                direction = True
            else:
                direction = False
            
            print(f"Trajectory Vector: dx={dist_x} m, dy={dist_y} m, angle={look_angle} rad")
            
            i2c.write_block(0x10, [dist_x, dist_y, look_angle], '=fff')

        # Show the processed frame
        # cv2.imshow('Frame', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # sleep(0.01)
        
        # with open("sensor_data.json", "a") as file:
        #     val = i2c.read_block(0x81, 12)
        
        #     data = struct.unpack("=fff", bytes(val))

        #     json_data = json.dumps({"floats": data})
            
        #     file.write(json_data)
        #     file.write("\n")
        #     file.flush()
        
        #     print(data)
        
        #     # sleep(0.5)

    cap.release()
    # cv2.destroyAllWindows()
    
    

if __name__ == "__main__":
    main()
