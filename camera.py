import stapipy as st
import numpy as np
import os
import cv2
from nodemaps.setting import set_enumeration
from nodemaps.node_values import *

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
        # 노드맵 설정 및 초기화
        self.nodemap = self.device.remote_port.nodemap
        # 픽셀 포맷 컨버터 설정
        self.st_converter_pixelformat = self.set_converter()
        # 트리거 모드 설정
        self.set_trigger_mode(nodemap=self.nodemap)
        # TriggerSoftware 모드의 Command 인터페이스 가져오기
        self.trigger_software = st.PyICommand(self.nodemap.get_node(TRIGGER_SOFTWARE))
        # 데이터 스트림 객체 생성
        self.datastream = self.device.create_datastream()       
    
    
    def start(self) -> None:
        """
        Start camera acquisition
        """
        
        self.datastream.start_acquisition()
        self.device.acquisition_start()
        
        print(f"Device {self.device.info.display_name} started")
    
    
    def datastream_callback(self, handle=None, context=None) -> None:
    # def datastream_callback(self, context=None) -> None:    #TODO: handle인자 없애고 해보기
        """
        데이터 스트림 이벤트가 발생했을 때 자동으로 실행되는 콜백 함수
        
        Args:
            handle: 이벤트를 트리거한 데이터 스트림 객체
            context: 콜백 등록 시 전달한 사용자 데이터
        """
        
        # 새로운 데이터 버퍼가 도착했을 때 발생하는 이벤트
        if handle.callback_type == st.EStCallbackType.GenTLDataStreamNewBuffer:
            try:
                # 0으로 해야 버퍼를 즉시 가져오기 위함, 불필요한 대기 시간을 줄이고 빠르게 다음 작업 수행 가능
                with self.datastream.retrieve_buffer(0) as st_buffer:
                    # 버퍼에 이미지가 있는지 확인
                    if st_buffer.info.is_image_present == True:
                        # 이미지 객체 생성
                        st_image = st_buffer.get_image()
                        # 이미지 변환
                        st_image = self.st_converter_pixelformat.convert(st_image)
                        # 로깅
                        print(f"BlockID={st_buffer.info.frame_id} Size={st_image.width} x {st_image.height} First Byte={st_image.get_image_data()[0]}")
                        # raw 이미지를 numpy 배열로 변환
                        st_image = self.raw_to_numpy(image=st_image)
                        # 이미지 저장
                        self.save_image(img_array=st_image, frame_id=st_buffer.info.frame_id)
                    else:
                        # # 버퍼에 이미지가 없는 경우
                        print("Image data does not exist.")
            except st.PyStError as exception:
                print("An exception occurred.", exception)
    
    
    def get_image(self) -> None:
        """
        Get image from camera
        
        # 트리거 모드 사용하지 않을 경우 이 메소드 사용
        """
        
        while self.datastream.is_grabbing:
            with self.datastream.retrieve_buffer(0) as buffer:   # with ~ as 구문으로 버퍼를 자동으로 해제
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
        카메라 객체 종료
        """
        
        self.device.acquisition_stop()
        self.datastream.stop_acquisition()
        set_enumeration(self.nodemap, TRIGGER_MODE, TRIGGER_MODE_OFF)
        print(f"Device {self.device.info.display_name} stopped")
    
    
    def set_converter(self, isColor:bool=True) -> st.PyStConverter:
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


    def raw_to_numpy(self, image:st.PyStImage):
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
        cv2.imwrite(filename=fileName, img=img_array)
        print(f"Image saved: {fileName}")
    
    
    def set_trigger_mode(self, nodemap) -> None: #TRY: nodemap을 인자로 받으면 nodemap이 적용되는지 확인하기
        """
        TriggerMode 설정
        """
        
        try:
            # FrameStart 트리거는 새로운 프레임의 캡처를 시작할 때 발생함
            # 이 트리거는 카메라가 새로운 이미지를 캡처하기 시작할 때 활성화
            # 일반적으로 프레임 기반 캡처를 제어하는 데 사용됨
            set_enumeration(nodemap, TRIGGER_SELECTOR, TRIGGER_SELECTOR_FRAME_START)
        except st.PyStError:
            # ExposureStart 트리거는 이미지 센서가 노출을 시작할 때 발생함
            # 이 트리거는 이미지 센서가 빛을 감지하기 시작할 때 활성화
            # 노출 시간과 관련된 작업을 제어하는 데 사용됨
            set_enumeration(nodemap, TRIGGER_SELECTOR, TRIGGER_SELECTOR_EXPOSURE_START)

        # Set the TriggerMode to On.
        set_enumeration(nodemap, TRIGGER_MODE, TRIGGER_MODE_ON)

        # Set the TriggerSource to Software
        set_enumeration(nodemap, TRIGGER_SOURCE, TRIGGER_SOURCE_SOFTWARE)



if __name__ == "__main__":
    st.initialize()
    st_system = st.create_system()
    
    cam1 = Camera(st_system=st_system)
    cb_func = cam1.datastream_callback   # 콜백 함수 가져오기
    callback = cam1.datastream.register_callback(cb_func)   # 데이터 스트림 콜백 등록
    
    cam1.start()
    # cam1.get_image()  # 트리거 모드 사용하지 않을 경우 이 메소드 사용
    while True:
            print("0 : Generate trigger")
            print("Else : Exit")
            selection = input("Select : \n")
            if selection == '0':
                cam1.trigger_software.execute()
            else:
                break
    cam1.stop()