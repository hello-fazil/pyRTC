#!/usr/bin/env python3

from pyrtc.video_transceiver import VideoTransceiver
import time
import asyncio

if __name__ == "__main__":
    video_handle = VideoTransceiver('answer')
    video_handle.startup()
    time.sleep(3)
    while True:
        for k in video_handle.data_channels.keys():
            print(f"[{k}] {video_handle.get_data(k)}")
