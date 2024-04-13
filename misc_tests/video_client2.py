#!/usr/bin/env python3

from pyrtc.transceiver import Trasceiver
import time
from pyrtc.helpers import deserialize_from_compressed_string

if __name__ == "__main__":
    transceiver = Trasceiver('answer')
    transceiver.startup()
    time.sleep(5)
    while True:
        for k in transceiver.data_channels.keys():
            print(f"[{k}] {deserialize_from_compressed_string(transceiver.get_data(k))}")
