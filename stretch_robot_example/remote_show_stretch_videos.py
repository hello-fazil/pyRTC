#!/usr/bin/env python3
from helpers import show_received

tracks = [('navigation_camera',(720, 1280, 3)),
          ('d435i_color_video',(720, 1280, 3)),
          ('d405_color_video',(480, 640, 3))]
show_received(tracks)