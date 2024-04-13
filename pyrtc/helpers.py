import multiprocessing.shared_memory
import numpy as np
import cv2
from copy import deepcopy
from pprint import pprint
import time
import sys
import json
import lzma
import base64

def create_shared_memory_video_frame(name,frame_shape, write=True):
    img = np.zeros(frame_shape, dtype=np.uint8)
    frame_shape = img.shape
    frame_dtype = img.dtype
    if write:
        shm = multiprocessing.shared_memory.SharedMemory(name=name,create=True, size=img.nbytes)
    else:
        shm = multiprocessing.shared_memory.SharedMemory(name=name,create=False)
    shared_frame = np.ndarray(frame_shape, dtype=frame_dtype, buffer=shm.buf)
    print(f"Created Video Buffer:\nshm_name: {shm.name}\nshm_shape: {frame_shape}\nshm_dtype: {frame_dtype}")
    return shm, shared_frame

def get_video_frame_bytes(frame):
    bytes_per_pixel = frame.format.bytes_per_pixel
    width = frame.width
    height = frame.height
    return bytes_per_pixel * width * height

try:
    import pyrealsense2 as rs
    def get_rs_devices():
        realsense_ctx = rs.context() 
        connected_devices = {}

        for i in range(len(realsense_ctx.devices)):
            camera_name = realsense_ctx.devices[i].get_info(rs.camera_info.name)
            camera_serial = realsense_ctx.devices[i].get_info(rs.camera_info.serial_number)
            connected_devices[camera_name] = camera_serial
        return connected_devices
except Exception as e:
    pass

"""
[RTCRtpCodecCapability(mimeType='video/VP8', clockRate=90000, channels=None, parameters={}),
 RTCRtpCodecCapability(mimeType='video/rtx', clockRate=90000, channels=None, parameters={}), 
 RTCRtpCodecCapability(mimeType='video/H264', clockRate=90000, channels=None, parameters={'level-asymmetry-allowed': '1', 'packetization-mode': '1', 'profile-level-id': '42001f'}), 
 RTCRtpCodecCapability(mimeType='video/H264', clockRate=90000, channels=None, parameters={'level-asymmetry-allowed': '1', 'packetization-mode': '1', 'profile-level-id': '42e01f'})]
"""
def force_codec(pc, sender, forced_codec):
    from aiortc.rtcrtpsender import RTCRtpSender
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    print("\n-----------------------------------------------------------------------------")
    codecs = [codec for codec in codecs if codec.mimeType == forced_codec]
    transceiver.setCodecPreferences(
        codecs
    )
    print(f"Sender [track_id: {transceiver.sender.track.id}]")
    print(f"Forcing the following Codecs:")
    for c in codecs:
        pprint(c,compact=True)
    print("-----------------------------------------------------------------------------\n")


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

def show_received_shm_video_stream(video_track_names=[]):
    tracks = {}
    for n,s in video_track_names:
        shm, shared_frame = create_shared_memory_video_frame(n,s,write=False)
        tracks[n] = {'shm':shm,'frame':shared_frame}

    while True:
        for n in tracks.keys():
            cv2.imshow(n,deepcopy(tracks[n]['frame']))
        cv2.waitKey(10)

def loading_dots(message,n=5):
    for i in range(n):
        time.sleep(.5)
        sys.stdout.write('.')
        sys.stdout.flush()
    print(message)

import json
import lzma
import base64

def serialize_to_compressed_string(obj):
    # Serialize the object to a JSON string
    json_str = json.dumps(obj)
    
    # Compress the JSON string
    compressed_data = lzma.compress(json_str.encode('utf-8'))
    
    # Encode the compressed data to Base64
    b64_encoded = base64.b64encode(compressed_data).decode('utf-8')
    
    return b64_encoded

def deserialize_from_compressed_string(comp_str):
    # Decode the Base64 encoded string
    compressed_data = base64.b64decode(comp_str.encode('utf-8'))
    
    # Decompress the data
    json_str = lzma.decompress(compressed_data).decode('utf-8')
    
    # Deserialize the JSON string back to an object
    obj = json.loads(json_str)
    
    return obj