#!/usr/bin/env python3
from pyrtc.helpers import show_received_shm_video_stream

tracks = [('my_web_cam',(720, 1280, 3))]
show_received_shm_video_stream(tracks)