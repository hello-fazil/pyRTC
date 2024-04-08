import numpy
import cv2
import numpy
from helpers import create_shared_memory_video_frame
import time

frame_shape = (480, 640, 3) #(720, 1280, 3)
recieved_image1 = numpy.zeros(frame_shape, dtype=numpy.uint8)
recieved_image2 = numpy.zeros(frame_shape, dtype=numpy.uint8)
recieved_image3 = numpy.zeros(frame_shape, dtype=numpy.uint8)

shm1, shared_frame1 = create_shared_memory_video_frame('video0',frame_shape,write=False)
shm2, shared_frame2 = create_shared_memory_video_frame('video1',frame_shape,write=False)
shm3, shared_frame3 = create_shared_memory_video_frame('ball_video',frame_shape,write=False)

def show_received():
    # global recieved_image
    while True:
        numpy.copyto(recieved_image1,shared_frame1)
        numpy.copyto(recieved_image2,shared_frame2)
        numpy.copyto(recieved_image3,shared_frame3)
        cv2.imshow("Received 1",recieved_image1)
        cv2.imshow("Received 2",recieved_image2)
        cv2.imshow("Received 3",recieved_image3)
        cv2.waitKey(10)


show_received()