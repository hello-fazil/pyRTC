#!/usr/bin/env python3
from pyrtc.helpers import create_shared_memory_video_frame, deepcopy, cv2
import time

def show_received(video_track_names=[]):
    tracks = {}
    for n,s,r in video_track_names:
        shm, shared_frame = create_shared_memory_video_frame(n,s,write=False)
        tracks[n] = {'shm':shm,'frame':shared_frame, 'rotate': r}

    while True:
        for n in tracks.keys():
            if tracks[n]['rotate']==0:
                cv2.imshow(n,deepcopy(tracks[n]['frame']))
            elif tracks[n]['rotate']==1:
                 cv2.imshow(n, cv2.rotate(deepcopy(tracks[n]['frame']), cv2.ROTATE_90_COUNTERCLOCKWISE))
            elif tracks[n]['rotate']==-1:
                 cv2.imshow(n, cv2.rotate(deepcopy(tracks[n]['frame']), cv2.ROTATE_90_CLOCKWISE))
        cv2.waitKey(10)
        time.sleep(0.001)

tracks = [('navigation_camera',(720, 1280, 3),1),
          ('d435i_color_video',(720, 1280, 3),-1),
          ('d405_color_video',(480, 640, 3),0)]
show_received(tracks)