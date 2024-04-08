import argparse
import asyncio
import logging
import math
import time
import cv2
import numpy
from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
    MediaStreamTrack,
    jitterbuffer
)
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling, TcpSocketSignaling
from av import VideoFrame
from av.video import reformatter
import os
import threading
from copy import deepcopy
from helpers import create_shared_memory_video_frame, get_video_frame_bytes

def setup_uvc_camera(device_index, size=None, fps=None, format = None):
    """
    Returns Opencv capture object of the UVC video divice
    """
    cap = cv2.VideoCapture(device_index)
    if format:
        fourcc_value = cv2.VideoWriter_fourcc(*f'{format}')
        cap.set(cv2.CAP_PROP_FOURCC, fourcc_value)
    if size:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, size[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size[1])
    if fps:
        cap.set(cv2.CAP_PROP_FPS, fps)
    return cap


class AbsVideoStreamTrack(VideoStreamTrack):
    def __init__(self, track_id, video_shape):
        super().__init__()  # don't forget this!
        self._id = track_id
        self.stop_uvc_stream = False
        self.data =  numpy.zeros(video_shape, dtype=numpy.uint8)
        sample_frame = VideoFrame.from_ndarray(self.data)
        print("\n-----------------------------------------------------------------------------")
        print(f"Starting {self.__class__.__name__} Stream [track_id: {track_id}]")
        print(f"buffer_size: {sample_frame.planes[0].buffer_size} line_size: {sample_frame.planes[0].line_size} height: {sample_frame.planes[0].height} width: {sample_frame.planes[0].width}")
        print("-----------------------------------------------------------------------------\n")
    
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        frame = VideoFrame.from_ndarray(
                                    self.data, format="bgr24"
                                )
        frame.pts = pts
        frame.time_base = time_base
        return frame
    
    def update_image(self,data):
        self.data = deepcopy(data)

class ReceivedVideoTrack(MediaStreamTrack):
    """
    Media Stream Track Handling Class which is used to Append received stream to the Queue

    Arguments:
    MediaStreamTrack : Media Stream Track holding Parent Class 
    """

    kind = "video"

    def __init__(self, track):
        # Initialize with Super to avoid reffering to Parent Clase
        super().__init__() 
        self.track = track
        self.received_image = None
        self.jitter_buffer = jitterbuffer.JitterBuffer(capacity=2,prefetch=2,is_video=True)
        print("\n-----------------------------------------------------------------------------")
        print(f"Receiving Video Track [track_id: {track.id}]")
        print(f"Read the frames from shared memory name: {track.id}")
        self.shm, self.shared_frame = create_shared_memory_video_frame(track.id,(720, 1280, 3))
        print("\n-----------------------------------------------------------------------------")
        self.share_thread = threading.Thread(target=self._share,daemon=True)
        self.share_thread.start()

    def _share(self):
        while True:
            try:
                numpy.copyto(self.shared_frame,self.received_image)
            except Exception as e:
                e = 0

    async def recv(self):
        frame = await self.track.recv()
        self.received_image = frame.to_ndarray(format="bgr24")
        print(f"[Video receive: {self.track.id}]  {self.received_image.shape} {self.received_image.mean()}")
        return frame
    
    def stop(self):
        super().stop()
        self.shm.close()
        self.shm.unlink()

class USBCameraStreamTrack(VideoStreamTrack):
    def __init__(self, track_id, VIDEO_INDEX, SIZE=None, FPS=None, VIDEO_FORMAT=None):
        super().__init__() 
        self._id = track_id
        self.uvc_camera = setup_uvc_camera(VIDEO_INDEX, SIZE, FPS, VIDEO_FORMAT)
        self.stop_uvc_stream = False
        self.uvc_image =  numpy.zeros((SIZE[0], SIZE[1], 3), dtype=numpy.uint8)
        sample_frame = VideoFrame.from_ndarray(self.uvc_image)
        self.frame = sample_frame
        print("\n-----------------------------------------------------------------------------")
        print(f"Starting USB Camera Stream [track_id: {track_id}]")
        print(f"buffer_size: {sample_frame.planes[0].buffer_size} line_size: {sample_frame.planes[0].line_size} height: {sample_frame.planes[0].height} width: {sample_frame.planes[0].width}")
        print("-----------------------------------------------------------------------------\n")
        self.uvc_stream_thread = threading.Thread(target=self.uvc_cam_stream,daemon=True)
        self.uvc_stream_thread.start()

    def uvc_cam_stream(self):
        while not self.stop_uvc_stream:
            try:
                ret, self.uvc_image = self.uvc_camera.read()
            except Exception as e:
                print(f"Error UVC Cam: {e}")
        self.uvc_camera.release()
    
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        # frame = deepcopy(self.frame)
        frame = VideoFrame.from_ndarray(
                                    self.uvc_image, format="bgr24"
                                )
        frame.pts = pts
        frame.time_base = time_base
        print(f"[USB cam send: {self._id}] {self.uvc_image.shape} {self.uvc_image.mean()}")
        return frame

async def run(pc, player, recorder, signaling, role, video_transmit_tracks):
    def add_tracks():
        if player and player.audio:
            pc.addTrack(player.audio)

        if player and player.video:
            pc.addTrack(player.video)
        else:
            if len(video_transmit_tracks.keys()):
                for t in video_transmit_tracks:
                    pc.addTrack(video_transmit_tracks[t])

    @pc.on("track")
    def on_track(track):
        print("Receiving %s" % track.kind)
        recorder.addTrack(ReceivedVideoTrack(track))
        # recorder.addTrack(track)

    # connect signaling
    await signaling.connect()

    if role == "offer":
        # send offer
        add_tracks()
        await pc.setLocalDescription(await pc.createOffer())
        await signaling.send(pc.localDescription)

    # consume signaling
    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            await recorder.start()

            if obj.type == "offer":
                # send answer
                add_tracks()
                await pc.setLocalDescription(await pc.createAnswer())
                await signaling.send(pc.localDescription)
        elif isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)
        elif obj is BYE:
            print("Exiting")
            break

class VideoTransceiver:
    def __init__(self, role,host='0.0.0.0',port=1234):
        # create signaling and peer connection
        # self.signaling = create_signaling(args)
        self.role = role
        self.signaling = TcpSocketSignaling(host, port)
        self.player = None
        self.pc = RTCPeerConnection()
        self.async_event_loop = asyncio.new_event_loop()
        self.tracks = {}
        self.recorder = MediaBlackhole()

        self.video_transmit_tracks = {}

    def run(self):
        self.async_event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.async_event_loop)
        # run event loop
        try:
           self.async_event_loop.run_until_complete(
                run(
                    pc=self.pc,
                    player=self.player,
                    recorder=self.recorder,
                    signaling=self.signaling,
                    role=self.role,
                    video_transmit_tracks=self.video_transmit_tracks,
                )
            )
        except KeyboardInterrupt:
            pass
        finally:
            # cleanup
            self.async_event_loop.run_until_complete(self.recorder.stop())
            self.async_event_loop.run_until_complete(self.signaling.close())
            self.async_event_loop.run_until_complete(self.pc.close())
            self.async_event_loop.stop()
    
    def addVideoTransmitFeed(self,video_track):
        self.video_transmit_tracks[video_track._id] = video_track

    async def signal_connect(self):
        await self.signaling.connect()

    def startup(self):
        t = threading.Thread(target=self.run)
        t.start()
    
    def stop():
        pass