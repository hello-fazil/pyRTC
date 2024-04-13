#!/usr/bin/env python3

from pyrtc.video_transceiver import VideoTransceiver, AbstractVideoStreamTrack
from pyrtc.helpers import setup_uvc_camera, loading_dots
import time
import sys

if __name__ == "__main__":

    # Initiate a Video Transceiver with a role (offer/answer) and host/port for TCP Signaling
    video_transceiver = VideoTransceiver('offer')
    codec_preference = 'video/H264' # 'video/VP8' 'video/rtx' 'video/H264 '
    video_transceiver.set_video_codec_preference(codec_preference)
    # Add a 'my_web_cam' feed to send to the connect peer video transceiver
    video_transceiver.addVideoTransmitFeed(AbstractVideoStreamTrack(track_id='my_web_cam', video_shape=(720, 1280, 3)))
    video_transceiver.addDataChannel('my_data_1')
    video_transceiver.addDataChannel('my_data_2')

    webcam = setup_uvc_camera('/dev/video0',size=[1280, 720])

    video_transceiver.startup()
    video_transceiver.wait_for_connection()
    counter = 0
    while video_transceiver.pc.connectionState=='connected':
        try:
            # Grab the video frames from the webcam
            ret, nav_head_image = webcam.read()
            # Update frames using the update_image() method for each transmitting tracks stored in the dictionary
            video_transceiver.video_transmit_tracks['my_web_cam'].update_image(nav_head_image)

            counter = counter + 1
            video_transceiver.send_data('my_data_1',f'[{time.time()}] count={counter}')

            counter = counter + 1
            video_transceiver.send_data('my_data_2',f'[{time.time()}] count={counter}')
            
        except Exception as e:
            print(f"Error webcam Stream: {e}")

    video_transceiver.stop()