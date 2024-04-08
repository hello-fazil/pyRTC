import multiprocessing.shared_memory
import numpy as np


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