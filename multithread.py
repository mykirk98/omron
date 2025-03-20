import threading
import stapipy as st
import cv2
import numpy as np
import sys
import select

class CameraThread(threading.Thread):
    def __init__(self, device):
        threading.Thread.__init__(self)
        self.device = device
        self.running = True
    
    def run(self):
        # 데이터 스트림 생성
        datastream = self.device.create_datastream()
        datastream.start_acquisition()
        self.device.acquisition_start()
        
        while self.running:
            with datastream.retrieve_buffer() as buffer:
                if buffer.info.is_image_present:
                    image = buffer.get_image()
                    print(f"BlockID : {buffer.info.frame_id} Size : {image.width} x {image.height} First Byte : {image.get_image_data()[0]}")
                    
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        self.running = False
        
        self.device.acquisition_stop()
        datastream.stop_acquisition()

if __name__ == "__main__":
    st.initialize()
    st_system = st.create_system()
    device_list = []
    
    while True:
        try:
            device = st_system.create_first_device()
            device_list.append(device)
        except:
            break
    
    threads = []
    for device in device_list:
        thread = CameraThread(device=device)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()