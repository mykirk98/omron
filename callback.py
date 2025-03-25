import stapipy as st
import threading

class CallBack:
    """
    이벤트 기반 콜백 클래스
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
            duplicate = self._image.copy()
        
        self._lock.release()
        
        return duplicate
    
    
    def datastream_callback(self, handle=None, context=None):
        """
        데이터 스트림 이벤트가 발생했을 때 자동으로 실행되는 콜백 함수
        
        Args:
            hnadle: 이벤트를 트리거한 데이터 스트림 객체
            context: 콜백 등록 시 전달한 사용자 데이터
        """
        
        st_datastream = handle.module
        
        # 데이터 스트림 객체가 존재하는 경우
        if st_datastream:
            # with 구문을 사용하여 버퍼를 자동으로 해제
            with st_datastream.retrieve_buffer() as st_buffer:
                # 버퍼가 이미지 데이터를 포함하는지 확인
                if st_buffer.info.is_image_present == True:
                    # 이미지 객체 생성
                    st_image = st_buffer.get_image()
                    print(f"BlockID : {st_buffer.info.frame_id} Size : {st_image.width} x {st_image.height} First Byte : {st_image.get_image_data()[0]}")
                else:
                    print("Image data does not exist")


if __name__ == '__main__':
    my_callback = CallBack()
    
    callback_func = my_callback.datastream_callback
    # callback_func = my_callback.datastream_callback(handle=None, context=None)
    
    print(callback_func)
    
    st.initialize()
    st_system = st.create_system()
    st_device = st_system.create_first_device()
    
    st_datastream = st_device.create_datastream()
    
    callback = st_datastream.register_callback(callback_func)
    
    st_datastream.start_acquisition()
    st_device.acquisition_start()
    
    input('Press Enter to terminate\n')
    
    st_device.acquisition_stop()
    st_datastream.stop_acquisition()
    st.terminate()