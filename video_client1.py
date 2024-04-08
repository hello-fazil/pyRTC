#!/usr/bin/env python3

from video_transceiver import VideoTransceiver, USBCameraStreamTrack, AbsVideoStreamTrack
import time
import asyncio
import numpy as np
import cv2



if __name__ == "__main__":
    UVC_COLOR_SIZE = [640, 480] # [3840,2880] [1920, 1080] [1280, 720] [640, 480]
    UVC_FPS = 24
    UVC_VIDEO_FORMAT = 'MJPG' # YUYV MJPG
    video_handle = VideoTransceiver(role='offer')
    video_handle.addVideoTransmitFeed(USBCameraStreamTrack(track_id='video0',
                                                           VIDEO_INDEX='/dev/video0', 
                                                           SIZE=UVC_COLOR_SIZE, 
                                                           FPS=UVC_FPS, 
                                                           VIDEO_FORMAT=UVC_VIDEO_FORMAT))
    # video_handle.addVideoTransmitFeed(USBCameraStreamTrack(track_id='video1',
    #                                                        VIDEO_INDEX='/dev/video3', 
    #                                                        SIZE=UVC_COLOR_SIZE, 
    #                                                        FPS=UVC_FPS, 
    #                                                        VIDEO_FORMAT=UVC_VIDEO_FORMAT))
    video_handle.addVideoTransmitFeed(AbsVideoStreamTrack(track_id='ball_video',
                                                          video_shape=(480, 640, 3)))
    video_handle.startup()


    # Stream a Bouncing Ball animation constructed live into 'ball_video' track
    while True:
        # Window size
        width, height = 640, 480

        # Ball settings
        ball_pos = np.array([width // 2, height // 2])
        ball_speed = np.array([2, 3])
        ball_radius = 20
        ball_color = (255, 0, 0)  # Blue in BGR
        img = np.zeros((height, width, 3), dtype=np.uint8)

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
            video_handle.video_transmit_tracks['ball_video'].update_image(img)
            time.sleep(0.01)
