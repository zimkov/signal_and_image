import cv2
import numpy as np

backSub_mog = cv2.createBackgroundSubtractorMOG2()

# Open camera
cap = cv2.VideoCapture(0)

while True:
    # Read image
    ret, img = cap.read()
    img = cv2.resize(img, (640, 480))

    # Apply background subtraction
    fg_mask = backSub_mog.apply(img)

    # Find contours
    contours, hierarchy = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Define minimum contour area
    min_contour_area = 5000
    large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_contour_area]

    # Create a mask for the large contours
    mask = np.zeros_like(img)  # Create a black mask
    cv2.drawContours(mask, large_contours, -1, (255, 255, 255),
                     thickness=cv2.FILLED)  # Fill the mask with white for the contours

    # Bitwise AND to keep only the moving objects
    frame_out = cv2.bitwise_and(img, mask)

    # Show the final frame
    cv2.imshow('Frame_final', frame_out)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close camera
cap.release()
cv2.destroyAllWindows()
