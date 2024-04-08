#!/usr/bin/env python3

from video_transceiver import VideoTransceiver, USBCameraStreamTrack
import time
import asyncio

if __name__ == "__main__":
    UVC_COLOR_SIZE = [640, 480] # [3840,2880] [1920, 1080] [1280, 720] [640, 480]
    UVC_FPS = 24
    UVC_VIDEO_FORMAT = 'YUYV' # YUYV MJPG
    video_handle = VideoTransceiver('answer')
    video_handle.addVideoTransmitFeed(USBCameraStreamTrack(track_id='video2',
                                                           VIDEO_INDEX='/dev/video2', 
                                                           SIZE=UVC_COLOR_SIZE, 
                                                           FPS=UVC_FPS, 
                                                           VIDEO_FORMAT=UVC_VIDEO_FORMAT))
    video_handle.startup()
    # while True:
    #     time.sleep(1)
    #     print( asyncio.run(video_handle.pc.getStats()))