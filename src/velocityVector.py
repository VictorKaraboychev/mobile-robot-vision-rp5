import cv2
import numpy as np
import math
from i2c_comms import I2CComms

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

    # Create masks for the red color range
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Apply morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour (assumed to be the red path)
        largest_contour = max(contours, key=cv2.contourArea)

        # Calculate the center of the largest contour
        moments = cv2.moments(largest_contour)
        if moments['m00'] > 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])

            # Get the bottom center of the frame (robot's perspective origin)
            height, width, _ = image.shape
            bottom_center = (width // 2, height)

            # Calculate trajectory vector (dx, dy)
            dx = cx - bottom_center[0]  # Horizontal offset (strafe direction)
            dy = bottom_center[1] - cy  # Vertical distance to the path end

            # Calculate the angle relative to the forward direction (0 degrees)
            angle = math.degrees(math.atan2(dx, dy))
            angle = math.floor(angle)

            # Visualize the path and trajectory vector on the frame
            cv2.circle(image, (cx, cy), 5, (0, 255, 0), -1)  # Path center
            cv2.line(image, bottom_center, (cx, cy), (255, 0, 0), 2)  # Trajectory vector
            cv2.drawContours(image, [largest_contour], -1, (0, 255, 255), 2)  # Path contour

            return dx, dy, angle

    return None  # Return None if no path is detected

# Main loop for processing video feed
def main():
    # Open the camera feed
    cap = cv2.VideoCapture(0)  # Change to the appropriate camera index if needed
    i2c = I2CComms(1, 0x8)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame for faster processing (optional)
        frame = cv2.resize(frame, (640, 480))

        # Get trajectory vector
        trajectory = get_trajectory_vector(frame)

        if trajectory:
            dx, dy, angle = trajectory
            dx = math.floor(np.interp(dx, [-320, 320], [0,255]))
            dy = math.floor(np.interp(dy, [0, 480], [0,255]))
            angle = math.floor(np.interp(angle, [0, 360], [0,255]))
            
            print(f"Trajectory Vector: dx={dx}, dy={dy}, angle={angle} degrees")
            
            i2c.write_block(0x00, [dx, dy, angle])

        # Show the processed frame
        cv2.imshow('Frame', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
