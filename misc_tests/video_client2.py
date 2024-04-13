#!/usr/bin/env python3

from pyrtc.video_transceiver import VideoTransceiver
import time
from pyrtc.helpers import deserialize_from_compressed_string

if __name__ == "__main__":
    video_handle = VideoTransceiver('answer')
    video_handle.startup()
    time.sleep(5)
    while True:
        for k in video_handle.data_channels.keys():
            print(f"[{k}] {deserialize_from_compressed_string(video_handle.get_data(k))}")
