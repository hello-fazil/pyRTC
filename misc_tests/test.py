import numpy
import cv2
import numpy
from helpers import create_shared_memory_video_frame
import time
from copy import deepcopy

frame_shape = (480, 640, 3) #(720, 1280, 3)

def show_received(video_track_names=[]):
    tracks = {}
    for n,s in video_track_names:
        shm, shared_frame = create_shared_memory_video_frame(n,s,write=False)
        tracks[n] = {'shm':shm,'frame':shared_frame}

    # global recieved_image
    while True:
        for n in tracks.keys():
            cv2.imshow(n,deepcopy(tracks[n]['frame']))
        cv2.waitKey(10)

tracks = [('ball_video',(480, 640, 3)),('video0',(480, 640, 3))]
show_received(tracks)