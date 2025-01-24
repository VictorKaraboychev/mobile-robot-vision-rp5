import cv2
import numpy as np
import math

def get_position_vectors(image):
    """
    Processes the given image, detects the red path, and calculates a set of position vectors.

    :param image: The input frame from the robot's camera
    :return: List of (x, y) position vectors in image coordinates
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

    position_vectors = []

    if contours:
        # Find the largest contour (assumed to be the red path)
        largest_contour = max(contours, key=cv2.contourArea)

        # Approximate the path as a series of points
        epsilon = 0.01 * cv2.arcLength(largest_contour, True)
        approx = cv2.approxPolyDP(largest_contour, epsilon, True)

        # Calculate position vectors from the bottom center of the frame
        height, width, _ = image.shape
        bottom_center = (width // 2, height)

        for point in approx:
            x, y = point[0]
            dx = x - bottom_center[0]  # Horizontal offset
            dy = bottom_center[1] - y  # Vertical offset (distance to move forward)
            position_vectors.append((dx, dy))

            # Visualize the point on the frame
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)  # Path point

        # Draw the contour and the approximated path
        cv2.drawContours(image, [largest_contour], -1, (0, 255, 255), 2)
        for i in range(len(approx) - 1):
            cv2.line(image, tuple(approx[i][0]), tuple(approx[i + 1][0]), (255, 0, 0), 2)

    return position_vectors

# Main loop for processing video feed
def main():
    # Open the camera feed
    cap = cv2.VideoCapture(0)  # Change to the appropriate camera index if needed

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame for faster processing (optional)
        frame = cv2.resize(frame, (640, 480))

        # Get position vectors
        position_vectors = get_position_vectors(frame)

        if position_vectors:
            print(f"Position Vectors: {position_vectors}")

        # Show the processed frame
        cv2.imshow('Frame', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
