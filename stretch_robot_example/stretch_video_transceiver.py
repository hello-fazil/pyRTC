#!/usr/bin/env python3
from pyrtc.video_transceiver import VideoTransceiver, AbstractVideoStreamTrack
import numpy as np
import stretch_body.hello_utils as hu
from pyrtc.helpers import get_rs_devices

if __name__ == "__main__":

    # Initiate a Video Transceiver with a role (offer/answer) and host/port for TCP Signaling
    video_transceiver = VideoTransceiver(role='offer',host='0.0.0.0',port=5555)


    # Add abstract video stream track for each video feed with an unique track_id 
    video_transceiver.addVideoTransmitFeed(AbstractVideoStreamTrack(track_id='navigation_camera', video_shape=(720, 1280, 3)))
    video_transceiver.addVideoTransmitFeed(AbstractVideoStreamTrack(track_id='d435i_color_video', video_shape=(720, 1280, 3)))
    video_transceiver.addVideoTransmitFeed(AbstractVideoStreamTrack(track_id='d405_color_video',  video_shape=(480, 640, 3)))

    codec_preference = 'video/H264' # 'video/VP8' 'video/rtx' 'video/H264 '
    video_transceiver.set_codec_preference(codec_preference)

    UVC_COLOR_SIZE = [1280, 720] # [3840,2880] [1920, 1080] [1280, 720] [640, 480]
    UVC_FPS = 100
    UVC_VIDEO_FORMAT = 'MJPG' # YUYV MJPG

    D405_COLOR_SIZE = [640, 480]
    D405_DEPTH_SIZE = [640, 480]
    D405_FPS = 15

    D435I_COLOR_SIZE = [1280, 720]
    D435I_DEPTH_SIZE = [1280, 720]
    D435I_FPS = 30

    


    # Create device handles for grabbing video frames from the robot
    pipeline_d405 = hu.setup_realsense_camera(serial_number=get_rs_devices()['Intel RealSense D405'],
                                              color_size=D405_COLOR_SIZE,
                                              depth_size=D405_DEPTH_SIZE,
                                              fps=D405_FPS)
    pipeline_d435i = hu.setup_realsense_camera(serial_number=get_rs_devices()['Intel RealSense D435I'],
                                               color_size=D435I_COLOR_SIZE,
                                               depth_size=D435I_DEPTH_SIZE,
                                               fps=D435I_FPS)
    nav_head_camera = hu.setup_uvc_camera('/dev/hello-nav-head-camera', UVC_COLOR_SIZE, UVC_FPS, UVC_VIDEO_FORMAT)


    def gather_streams_step():
        try:
            # Grab the video frames from the robot devices
            frames_d435i = pipeline_d435i.wait_for_frames()
            color_frame_d435i = frames_d435i.get_color_frame()
            frames_d405 = pipeline_d405.wait_for_frames()
            color_frame_d405 = frames_d405.get_color_frame()
            ret, nav_head_image = nav_head_camera.read()

            # Update frames using the update_image() method for each transmitting tracks stored in the dictionary
            video_transceiver.video_transmit_tracks['d435i_color_video'].update_image(np.asanyarray(color_frame_d435i.get_data()))
            video_transceiver.video_transmit_tracks['d405_color_video'].update_image(np.asanyarray(color_frame_d405.get_data()))
            video_transceiver.video_transmit_tracks['navigation_camera'].update_image(nav_head_image)
        except Exception as e:
            print(f"Error Camera Streams: {e}")
    
    # Start the video transceiver thread 
    video_transceiver.startup()

    # Update the video frames in main loop
    while True:
        gather_streams_step()
        

