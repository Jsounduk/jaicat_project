import cv2
import numpy as np

# Load the video capture device (e.g. camera)
cap = cv2.VideoCapture(0)

# Set the video codec and create a video writer
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply a Gaussian blur to the grayscale image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Detect edges in the blurred image
    edges = cv2.Canny(blurred, 50, 150)
    
    # Find contours in the edge image
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Iterate through the contours and draw a rectangle around each one
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Write the output frame to the video file
    out.write(frame)
    
    # Display the output frame
    cv2.imshow('frame', frame)
    
    # Exit on key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and close the video writer
cap.release()
out.release()
cv2.destroyAllWindows()
