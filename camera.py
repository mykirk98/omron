import stapipy as st
import numpy as np
import os
import cv2

class Camera:
    """
    카메라 클래스
    """
    
    def __init__(self, st_system, isColor=True):
        """
        Args:
            st_system: stApi 시스템 객체
        """
        # Flags
        self.isColor = isColor
        
        # directory
        self.image_save_dir = "captured_images"
        os.makedirs(name=self.image_save_dir, exist_ok=True)
        
        
        self.device = st_system.create_first_device()   # 첫 번째 카메라 객체 생성
        self.datastream = self.device.create_datastream()   # 데이터 스트림 객체 생성
        
        self.callback = self.datastream.register_callback(self.datastream_callback)   # 콜백 등록
        
        # 노드맵 설정 및 초기화
        self.nodemap = self.device.remote_port.nodemap
        self.st_converter_pixelformat = self.set_converter()
    
    
    def start(self) -> None:
        """
        Start camera acquisition
        """
        
        self.datastream.start_acquisition()
        self.device.acquisition_start()
        
        print(f"Device {self.device.info.display_name} started")
    
    
    def get_image(self) -> None:
        """
        Get image from camera
        """
        
        while self.datastream.is_grabbing:
            with self.datastream.retrieve_buffer() as buffer:   # with ~ as 구문으로 버퍼를 자동으로 해제
                # 버퍼에 이미지가 있는지 확인
                if buffer.info.is_image_present:
                    image = buffer.get_image()
                    image = self.st_converter_pixelformat.convert(image)   # 이미지 변환
                    print(f"BlockID : {buffer.info.frame_id} Size : {image.width} x {image.height} Bytes : {image.get_image_data()[0]}")
                    image = self.raw_to_numpy(image=image)   # raw 이미지를 numpy 배열로 변환
                    self.save_image(img_array=image, frame_id=buffer.info.frame_id)
                else:
                    print("Image data does not exist")
    
    def stop(self) -> None:
        """
        Stop camera acquisition
        """
        
        self.device.acquisition_stop()
        self.datastream.stop_acquisition()
        print(f"Device {self.device.info.display_name} stopped")
    
    def set_converter(self):
        """
        stApi로 이미지 변환
        
        Return:
            st_converter_pixelformat: 변환된 이미지 객체
        """
        
        st_converter_pixelformat = st.create_converter(st.EStConverterType.PixelFormat)
        
        if self.isColor == True:
            st_converter_pixelformat.destination_pixel_format = st.EStPixelFormatNamingConvention.BGR8
        else:
            st_converter_pixelformat.destination_pixel_format = st.EStPixelFormatNamingConvention.Mono8
        
        return st_converter_pixelformat

    def raw_to_numpy(self, image:st.PyStImage):    #TODO: raw:st.image?
        """
        raw 이미지를 numpy 배열로 변환
        
        Args:
            raw: raw 이미지 객체
        
        Return:
            img_array: 변환된 이미지 넘파이 배열
        """
        
        width, height = image.width, image.height
        raw_image = image.get_image_data()
        
        # Numpy 배열로 변환
        img_array = np.array(raw_image, dtype=np.uint8)
        
        if self.isColor == True:
            img_array = img_array.reshape((height, width, 3))
        else:
            img_array = img_array.reshape((height, width))
        
        return img_array
        
    def save_image(self, img_array: np.ndarray, frame_id: int) -> None:
        """
        캡쳐된 이미지를 저장하는 메소드
        
        Args:
            img_array: 이미지 배열
            frame_id: 프레임 ID
        """
        
        fileName = os.path.join(self.image_save_dir, self.device.info.display_name + f"_{frame_id}.bmp")
        
        # 이미지 저장
        cv2.imwrite(fileName, img_array)
        print(f"Image saved: {fileName}")
    
    


if __name__ == "__main__":
    st.initialize()
    st_system = st.create_system()
    
    cam1 = Camera(st_system=st_system)
    cam1.start()
    # cam1.get_image()
    input("Press Enter to stop camera acquisition...\n")
    cam1.stop()