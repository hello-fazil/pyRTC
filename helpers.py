import multiprocessing.shared_memory
import numpy as np
import pyrealsense2 as rs
import stretch_body.hello_utils as hu

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

def get_rs_devices():
    realsense_ctx = rs.context() 
    connected_devices = {}

    for i in range(len(realsense_ctx.devices)):
        camera_name = realsense_ctx.devices[i].get_info(rs.camera_info.name)
        camera_serial = realsense_ctx.devices[i].get_info(rs.camera_info.serial_number)
        connected_devices[camera_name] = camera_serial
    return connected_devices