import cv2
import numpy as np

# Load the video stream
cap = cv2.VideoCapture(0)  # Change to your video source

# Camera intrinsic parameters (example values, replace with your calibration results)
camera_matrix = np.array([[700, 0, 320], [0, 700, 240], [0, 0, 1]])  # Example camera matrix
dist_coeffs = np.array([-0.2, 0.1, 0, 0])  # Example distortion coefficients (k1, k2, p1, p2)

# Resolution of the frame
frame_width = 640
frame_height = 480

# Generate rectification maps for an equidistant projection
new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (frame_width, frame_height), 1, (frame_width, frame_height))
mapx, mapy = cv2.initUndistortRectifyMap(camera_matrix, dist_coeffs, None, new_camera_matrix, (frame_width, frame_height), cv2.CV_32FC1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        break

    # Apply the rectification map
    equidistant_frame = cv2.remap(frame, mapx, mapy, interpolation=cv2.INTER_LINEAR)

    # Display the output
    cv2.imshow("Original", frame)
    cv2.imshow("Equidistant Frame", equidistant_frame)

    # Break loop on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video stream and close windows
cap.release()
cv2.destroyAllWindows()
