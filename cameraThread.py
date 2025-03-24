import stapipy as st
import threading
import os
import numpy as np
import cv2

class CameraThread(threading.Thread):
    """
    카메라 스레드 클래스: threading.Thread를 상속받아 독립적인 스레드에서 실행
    """

    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None, st_system):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        
        self.device = st_system.create_first_device()  # 첫 번째 카메라 장치 생성
        self.datastream = self.device.create_datastream()
        
        self.runningFlag = None  # 카메라 스레드 실행 여부 플래그

        self.image_save_dir = "captured_images"
        os.makedirs(name=self.image_save_dir, exist_ok=True)
        self.st_converter = self.convert_image()
    
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
                    self.image = buffer.get_image()
                    self.image = self.st_converter.convert(self.image)
                    print(f"BlockID : {buffer.info.frame_id} Size : {self.image.width} x {self.image.height} First Byte : {self.image.get_image_data()[0]}")
                    
                    self.save_image(image=self.image, frame_id=buffer.info.frame_id)
                else:
                    print("Image data does not exist")
                    
        
        self.device.acquisition_stop()
        self.datastream.stop_acquisition()
    
    
    def stop(self):
        """
        카메라 스레드 중지
        """
        
        self.runningFlag = False
        self.join()
        print(f"Device {self.device.info.display_name} stopped")
    
    
    def convert_image(self):
        """
        stApi로 이미지 변환

        Return:
            _image: 변환된 이미지 객체
        """
        
        st_converter_pixelformat = st.create_converter(st.EStConverterType.PixelFormat)
        st_converter_pixelformat.destination_pixel_format = st.EStPixelFormatNamingConvention.BGR8
        
        return st_converter_pixelformat
    
    
    def save_image(self, image, frame_id: int) -> None:
        """
        캡처된 이미지를 저장하는 메소드
        
        Args:
            image: 이미지 객체
            frame_id: 이미지의 프레임 ID
        """
        
        width, height = image.width, image.height
        raw_image = image.get_image_data()
        
        # Numpy 배열로 변환
        img_array = np.array(raw_image, dtype=np.uint8).reshape((height, width, 3))
        filename = os.path.join(self.image_save_dir, self.device.info.display_name + f"_{frame_id}.bmp")
        
        # 이미지 저장
        cv2.imwrite(filename, img_array)
        print(f"Image saved: {filename}")


if __name__ == "__main__":
    st.initialize()     # StApi 초기화
    st_system = st.create_system()
    
    camera_thread = CameraThread(st_system=st_system)
    camera_thread.start()
    
    input("Press Enter to stop...\n")
    
    camera_thread.stop()
    st.terminate()