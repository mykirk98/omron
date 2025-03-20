import stapipy as st
# import logging

class Camera:
    """
    카메라 클래스
    """
    
    def __init__(self, st_system):
        """
        Args:
            st_system: system object
        """
        self.device = st_system.create_first_device()
        self.datastream = self.device.create_datastream()
        self.runningFlag = None
    
    
    def start(self):
        """
        Start camera acquisition
        """
        self.runningFlag = True
        
        self.datastream.start_acquisition()
        self.device.acquisition_start()
        
        print(f"Device {self.device.info.display_name} started")
    
    
    def get_image(self):
        """
        Get image from camera
        """
        
        while self.runningFlag is True:
            with self.datastream.retrieve_buffer() as buffer:   # with ~ as 구문으로 버퍼를 자동으로 해제
                # 버퍼에 이미지가 있는지 확인
                if buffer.info.is_image_present:
                    image = buffer.get_image()
                    print(f"BlockID : {buffer.info.frame_id} Size : {image.width} x {image.height} Bytes : {image.get_image_data()[0]}")
                    # return image
                else:
                    print("Image data does not exist")
                    return 0
            # time.sleep(0.01)

    
    def stop(self):
        """
        Stop camera acquisition
        """
        
        self.runningFlag = False
        
        self.device.acquisition_stop()
        self.datastream.stop_acquisition()
        
        print(f"Device {self.device.info.display_name} stopped")


if __name__ == "__main__":
    st.initialize()
    st_system = st.create_system()
    
    cam1 = Camera(st_system=st_system)
    cam1.start()
    cam1.get_image()    #FIXME: 무한 루프 탈출 방법 필요
    cam1.stop()