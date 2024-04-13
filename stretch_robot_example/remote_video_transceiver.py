#!/usr/bin/env python3

from pyrtc.transceiver import Trasceiver, AbstractVideoStreamTrack
from pyrtc.helpers import setup_uvc_camera
import time
import asyncio
import yaml

if __name__ == "__main__":

    # Initiate a Video Transceiver with a role (offer/answer) and host/port for TCP Signaling
    transceiver = Trasceiver('answer',host='10.1.10.143',port=5555)
    
    # Add a 'my_web_cam' feed to send to the connect peer video transceiver
    # video_transceiver.addVideoTransmitFeed(AbstractVideoStreamTrack(track_id='my_web_cam', video_shape=(720, 1280, 3)))

    # webcam = setup_uvc_camera('/dev/video0',size=[1280, 720])

    transceiver.startup()
    # while True:
    #     try:
    #         # Grab the video frames from the webcam
    #         ret, nav_head_image = webcam.read()
    #         # Update frames using the update_image() method for each transmitting tracks stored in the dictionary
    #         video_transceiver.video_transmit_tracks['my_web_cam'].update_image(nav_head_image)
    #     except Exception as e:
    #         print(f"Error webcam Stream: {e}")