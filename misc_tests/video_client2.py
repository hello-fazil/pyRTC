#!/usr/bin/env python3

from pyrtc.video_transceiver import VideoTransceiver
import time
import asyncio

if __name__ == "__main__":
    video_handle = VideoTransceiver('answer')
    video_handle.startup()