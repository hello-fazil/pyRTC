import numpy as np
import cv2

# Window size
width, height = 640, 480

# Ball settings
ball_pos = np.array([width // 2, height // 2])
ball_speed = np.array([2, 3])
ball_radius = 20
ball_color = (255, 0, 0)  # Blue in BGR

# Create a window
cv2.namedWindow('Bouncing Ball')

while True:
    # Create a black image
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Update ball position
    ball_pos += ball_speed

    # Check for collision with the edges and bounce
    if ball_pos[0] <= ball_radius or ball_pos[0] >= width - ball_radius:
        ball_speed[0] = -ball_speed[0]
    if ball_pos[1] <= ball_radius or ball_pos[1] >= height - ball_radius:
        ball_speed[1] = -ball_speed[1]

    # Draw the ball
    cv2.circle(img, tuple(ball_pos), ball_radius, ball_color, -1)

    # Display the image
    cv2.imshow('Bouncing Ball', img)

    # Break the loop when 'ESC' is pressed
    if cv2.waitKey(10) == 27:
        break

# Close the window
cv2.destroyAllWindows()
