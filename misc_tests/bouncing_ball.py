#!/usr/bin/env python3

from video_transceiver import VideoTransceiver, USBCameraStreamTrack, AbstractVideoStreamTrack, RealsenseD435iStreamTrack, RealsenseD405StreamTrack
import time
import asyncio
import numpy as np
import cv2
import stretch_body.hello_utils as hu
from helpers import get_rs_devices
import threading

if __name__ == "__main__":
    UVC_COLOR_SIZE = [1280, 720] # [3840,2880] [1920, 1080] [1280, 720] [640, 480]
    UVC_FPS = 100
    UVC_VIDEO_FORMAT = 'MJPG' # YUYV MJPG

    D405_COLOR_SIZE = [640, 480]
    D405_DEPTH_SIZE = [640, 480]
    D405_FPS = 15

    D435I_COLOR_SIZE = [1280, 720]
    D435I_DEPTH_SIZE = [1280, 720]
    D435I_FPS = 15

    video_handle = VideoTransceiver(role='offer',host='10.1.10.143',port=5555)
    video_handle.addVideoTransmitFeed(USBCameraStreamTrack(track_id='video0',
                                                           VIDEO_INDEX='/dev/hello-nav-head-camera', 
                                                           SIZE=UVC_COLOR_SIZE, 
                                                           FPS=UVC_FPS, 
                                                           VIDEO_FORMAT=UVC_VIDEO_FORMAT))
    video_handle.addVideoTransmitFeed(AbstractVideoStreamTrack(track_id='ball_video',
                                                          video_shape=(1080, 1920, 3)))

    # video_handle.addVideoTransmitFeed(RealsenseD435iStreamTrack(track_id='d435i_color_video',
    #                                                             SIZE=D435I_COLOR_SIZE,
    #                                                             FPS=D435I_FPS))

    # video_handle.addVideoTransmitFeed(RealsenseD405StreamTrack(track_id='d405_color_video',
    #                                                             SIZE=D405_COLOR_SIZE,
    #                                                             FPS=D405_FPS))

    video_handle.addVideoTransmitFeed(AbstractVideoStreamTrack(track_id='d435i_color_video',
                                                          video_shape=(720, 1280, 3)))
    video_handle.addVideoTransmitFeed(AbstractVideoStreamTrack(track_id='d405_color_video',
                                                          video_shape=(480, 640, 3)))



    pipeline_d405 = hu.setup_realsense_camera(serial_number=get_rs_devices()['Intel RealSense D405'],
                                           color_size=D405_COLOR_SIZE,
                                            depth_size=D405_DEPTH_SIZE,
                                            fps=D405_FPS)
    pipeline_d435i = hu.setup_realsense_camera(serial_number=get_rs_devices()['Intel RealSense D435I'],
                                            color_size=D435I_COLOR_SIZE,
                                            depth_size=D435I_DEPTH_SIZE,
                                            fps=D435I_FPS)
    
    def realsense_stream_step():
        try:
            frames_d435i = pipeline_d435i.wait_for_frames()
            color_frame_d435i = frames_d435i.get_color_frame()
            video_handle.video_transmit_tracks['d435i_color_video'].update_image(np.asanyarray(color_frame_d435i.get_data()))
            frames_d405 = pipeline_d405.wait_for_frames()
            color_frame_d405 = frames_d405.get_color_frame()
            video_handle.video_transmit_tracks['d405_color_video'].update_image(np.asanyarray(color_frame_d405.get_data()))
        except Exception as e:
            print(f"Error Realsense Stream: {e}")
    
    class BouncingBallVideo:
        def __init__(self):
            # Window size
            self.width, self.height = 1920, 1080

            # Ball settings
            self.ball_pos = np.array([self.width // 2, self.height // 2])
            self.ball_speed = np.array([2, 3])*2
            self.ball_radius = 80
            self.ball_color = (255, 0, 0)  # Blue in BGR
            self.img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        def bouncing_ball_step(self):
            # Create a black image
            img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

            # Update ball position
            self.ball_pos += self.ball_speed

            # Check for collision with the edges and bounce
            if self.ball_pos[0] <= self.ball_radius or self.ball_pos[0] >= self.width - self.ball_radius:
                self.ball_speed[0] = -self.ball_speed[0]
            if self.ball_pos[1] <= self.ball_radius or self.ball_pos[1] >= self.height - self.ball_radius:
                self.ball_speed[1] = -self.ball_speed[1]

            # Draw the ball
            cv2.circle(img, tuple(self.ball_pos), self.ball_radius, self.ball_color, -1)
            video_handle.video_transmit_tracks['ball_video'].update_image(img)
    ball_video_gen = BouncingBallVideo()

    video_handle.startup()
    while True:
        realsense_stream_step()
        ball_video_gen.bouncing_ball_step()
        

