import stapipy as st
import threading
import time
import numpy as np
import cv2  # 이미지 저장을 위한 OpenCV

class CameraThread(threading.Thread):
    """
    카메라 스레드 클래스: threading.Thread를 상속받아 독립적인 스레드에서 실행
    """

    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None, st_system):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        
        self.device = st_system.create_first_device()  # 첫 번째 카메라 장치 생성
        self.datastream = self.device.create_datastream()
        
        self.runningFlag = None  # 카메라 스레드 실행 여부 플래그
    
    
    def run(self):
        """
        run() 메소드는 start() 메소드가 호출되면 자동으로 실행되는 메소드, Thread 클래스에서 오버라이딩하여 사용
        카메라 스레드 실행
        """
        
        self.runningFlag = True
        
        self.datastream.start_acquisition()
        self.device.acquisition_start()
        print(f"Device {self.device.info.display_name} started")
        
        while self.runningFlag is True:
            with self.datastream.retrieve_buffer() as buffer:
                if buffer.info.is_image_present == True:
                    image = buffer.get_image()
                    print(f"BlockID : {buffer.info.frame_id} Size : {image.width} x {image.height} First Byte : {image.get_image_data()[0]}")
                else:
                    print("Image data does not exist")
                    
            time.sleep(0.01)
        
        self.device.acquisition_stop()
        self.datastream.stop_acquisition()
    
    
    def stop(self):
        """
        카메라 스레드 중지
        """
        
        self.runningFlag = False
        self.join()
        print(f"Device {self.device.info.display_name} stopped")


if __name__ == "__main__":
    st.initialize()     # StApi 초기화
    st_system = st.create_system()
    
    camera_thread = CameraThread(st_system=st_system)
    camera_thread.start()
    
    input("Press Enter to stop...\n")
    
    camera_thread.stop()
    st.terminate()