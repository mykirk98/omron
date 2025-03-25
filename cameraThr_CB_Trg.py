import stapipy as st
import threading
import os
import numpy as np
import cv2
import tkinter as tk

class CameraThread(threading.Thread):
    """
    카메라 스레드 클래스,
        트리거 기능이 구현됨
    """

    def __init__(self, st_system, isColor=True):
        super().__init__()
        """
        Args:
            st_system: StApi 시스템 객체
            isColor: 컬러카메라 or 모노카메라 여부
        """
        self.runningFlag = None  # 카메라 스레드 실행 여부 플래그
        self.isColor = isColor  # 컬러카메라 or 모노카메라
        
        self.device = st_system.create_first_device()  # 첫 번째 카메라 장치 생성
        self.nodemap = self.device.remote_port.nodemap  # 노드맵 (카메라 설정)
        self.datastream = self.device.create_datastream()

        self.image_save_dir = "captured_images"
        os.makedirs(name=self.image_save_dir, exist_ok=True)
        
        self.st_converter = self.convert_image()

        # 트리거 설정
        self.configure_trigger()
    
    def configure_trigger(self):
        """
        소프트웨어 트리거 모드 활성화
        """
        self.set_enumeration(self.nodemap, "TriggerSelector", "FrameStart")
        self.set_enumeration(self.nodemap, "TriggerMode", "On")
        self.set_enumeration(self.nodemap, "TriggerSource", "Software")

        # 소프트웨어 트리거 노드 가져오기
        self.trigger_command = st.PyICommand(self.nodemap.get_node("TriggerSoftware"))
    
    def run(self):
        """
        run() 메소드는 start() 메소드가 호출되면 자동으로 실행되는 메소드, Thread 클래스에서 오버라이딩하여 사용
        카메라 스레드 실행
        """
        self.runningFlag = True
        
        self.datastream.start_acquisition()
        self.device.acquisition_start()
        print(f"Device {self.device.info.display_name} started")
        
        while self.runningFlag:
            with self.datastream.retrieve_buffer() as buffer:   # with 구문을 사용하여 버퍼를 자동으로 해제
                if buffer.info.is_image_present:
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

    def trigger(self):
        """
        소프트웨어 트리거 실행
        """
        print("Triggering camera...")
        self.trigger_command.execute()

    def convert_image(self):
        """
        stApi로 이미지 변환

        Return:
            _image: 변환된 이미지 객체
        """
        st_converter_pixelformat = st.create_converter(st.EStConverterType.PixelFormat)
        
        if self.isColor:
            st_converter_pixelformat.destination_pixel_format = st.EStPixelFormatNamingConvention.BGR8
        else:
            st_converter_pixelformat.destination_pixel_format = st.EStPixelFormatNamingConvention.Mono8
        
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
        img_array = np.array(raw_image, dtype=np.uint8)
        
        if self.isColor:
            img_array = img_array.reshape((height, width, 3))
        else:
            img_array = img_array.reshape((height, width))
        
        filename = os.path.join(self.image_save_dir, self.device.info.display_name + f"_{frame_id}.bmp")
        
        # 이미지 저장
        cv2.imwrite(filename, img_array)
        print(f"Image saved: {filename}")

    @staticmethod
    def set_enumeration(nodemap, enum_name, entry_name):
        """
        열거형 노드의 값을 설정하는 함수

        Args:
            nodemap: 카메라 설정을 위한 노드 맵
            enum_name:  열거형 노드의 심볼릭 값
            entry_name:  열거형 엔트리 노드의 심볼릭 값
        """
        # 열거형 노드 가져오기
        enum_node = st.PyIEnumeration(nodemap.get_node(enum_name))
        # 열거형 엔트리 노드 가져오기
        entry_node = st.PyIEnumEntry(enum_node[entry_name])
        # 열거형 노드의 값 설정
        enum_node.set_entry_value(entry_node)

class TriggerButtonApp:
    def __init__(self, root, camera_thread):
        self.root = root
        self.root.title("Trigger Button")

        self.camera_thread = camera_thread  # 카메라 스레드 객체 저장

        self.button = tk.Button(root, text="Trigger", command=self.on_button_click)
        self.button.pack()
        self.button.config(width=20, height=3)
        self.root.geometry("300x200")

    def on_button_click(self):
        print("Button clicked")
        self.camera_thread.trigger()  # 카메라 트리거 실행

    @classmethod
    def run(cls, camera_thread):
        root = tk.Tk()
        app = cls(root, camera_thread)
        root.mainloop()


if __name__ == "__main__":
    st.initialize()  # StApi 초기화
    st_system = st.create_system()
    
    camera_thread = CameraThread(st_system=st_system, isColor=True)
    camera_thread.start()
    
    # Tkinter 실행 (버튼 클릭하면 트리거 발생)
    TriggerButtonApp.run(camera_thread)
    
    input("Press Enter to stop...\n")
    
    camera_thread.stop()
    st.terminate()
