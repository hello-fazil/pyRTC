#!/usr/bin/env python3

from pyrtc.video_transceiver import VideoTransceiver, AbstractVideoStreamTrack
from pyrtc.helpers import setup_uvc_camera, serialize_to_compressed_string
import time

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
            data_1 = serialize_to_compressed_string({'time':time.time(),'count':counter})
            video_transceiver.send_data('my_data_1',data_1)

            counter = counter + 1
            data_2 = serialize_to_compressed_string({'time':time.time(),'count':counter})
            video_transceiver.send_data('my_data_2',data_2)
            
        except Exception as e:
            print(f"Error webcam Stream: {e}")

    video_transceiver.stop()