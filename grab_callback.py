import stapipy as st
import threading

class CMyCallback:
    """
    콜백 함수를 포함하는 클래스
    """
    def __init__(self):
        self._image = None
        self._lock = threading.Lock()
    
    @property
    def image(self):
        """
        획득한 이미지를 프로퍼티처럼 접근할 수 있게 해줌
        Lock을 사용하여 멀티스레드 환경에서 데이터가 손실되는 것을 방지
        
        duplicate : 복사본 반환
        """
        duplicate = None
        self._lock.acquire()    # 멀티스레드 환경에서 한 번에 하나의 스레드만 접근 가능하도록 설정
        
        if self._image is not None:
            duplicate = self._image.copy()  # 원본을 직접 반환하면 외부 코드에서 원본 데이터 접근 시 충돌 발생
            
        self._lock.release()    # 락을 해제하여 다른 스레드에 접근 허용
        
        return duplicate

    def datastream_callback(self, handle=None, context=None):
        """
        카메라에서 데이터 스트림 이벤트가 발생했을 때 자동으로 실행되는 콜백 함수
        
        handle : 이벤트를 트리거한 데이터 스트림 객체
        context : user data passed on during callback registration
        """
        
        st_datastream = handle.module
        if st_datastream:
            with st_datastream.retrieve_buffer() as st_buffer:  # with 구문을 사용하여 버퍼를 자동으로 해제
                # 버퍼가 이미지 데이터를 포함하는지 확인
                if st_buffer.info.is_image_present == True:
                    # 이미지 객체 생성
                    st_image = st_buffer.get_image()
                    print(f"BlockID : {st_buffer.info.frame_id} Size : {st_image.width} x {st_image.height} First Byte : {st_image.get_image_data()[0]}")
                else:
                    print("Image data does not exist")


if __name__ == "__main__":
    # Get the callback function
    my_callback = CMyCallback()
    callback_func = my_callback.datastream_callback
    
    try:
        st.initialize()
        st_system = st.create_system()
        st_device = st_system.create_first_device()
        
        # print(f"device : {st_device.info.display_name}")
        print(f"model : {st_device.info.model}")
        print(f"serial number : {st_device.info.serial_number}")
        print(f"device id : {st_device.info.device_id}")
        
        # Create a datastream object for handling image stream data
        st_datastream = st_device.create_datastream()
        
        # Register callback for datastream
        # callback = st_datastream.register_callback(datastream_callback) #NOTE: use when using callback function NOT callback class
        callback = st_datastream.register_callback(callback_func)
        
        st_datastream.start_acquisition(5)
        st_device.acquisition_start()
        
        input("Press enter to terminate")
        
        st_device.acquisition_stop()
        st_datastream.stop_acquisition()
    
    except Exception as exception:
        print(exception)