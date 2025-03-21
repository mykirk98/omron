import stapipy as st
import threading
import numpy as np
import cv2
from utils.device_info import print_info

DISPLAY_RESIZE_FACTOR = 0.5

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

    def datastream_callback_cv2(self, handle=None, context=None):
        """
        Callback to handle events from DataStream

        :param handle: handle that trigger the callback
        :param context: user data passed on during callback registration
        """
        st_datastream = handle.module
        if st_datastream:
            with st_datastream.retrieve_buffer() as st_buffer:
                # Check if the acquired data contains image data.
                if st_buffer.info.is_image_present:
                    # Create an image object.
                    st_image = st_buffer.get_image()

                    # Check the pixelformat of the input image.
                    pixel_format = st_image.pixel_format
                    pixel_format_info = st.get_pixel_format_info(pixel_format)

                    # Only mono or bayer is processed.
                    if not(pixel_format_info.is_mono or pixel_format_info.is_bayer):
                        return

                    # Get raw image data.
                    data = st_image.get_image_data()

                    # Perform pixel value scaling if each pixel component is
                    # larger than 8bit. Example: 10bit Bayer/Mono, 12bit, etc.
                    if pixel_format_info.each_component_total_bit_count > 8:
                        nparr = np.frombuffer(data, np.uint16)
                        division = pow(2, pixel_format_info.each_component_valid_bit_count - 8)
                        nparr = (nparr / division).astype('uint8')
                    else:
                        nparr = np.frombuffer(data, np.uint8)

                    # Process image for display.
                    nparr = nparr.reshape(st_image.height, st_image.width, 1)

                    # Perform color conversion for Bayer.
                    if pixel_format_info.is_bayer:
                        bayer_type = pixel_format_info.get_pixel_color_filter()
                        if bayer_type == st.EStPixelColorFilter.BayerRG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_RG2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerGR:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GR2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerGB:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GB2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerBG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_BG2RGB)

                    # Resize image and store to self._image.
                    nparr = cv2.resize(nparr, None, fx=DISPLAY_RESIZE_FACTOR, fy=DISPLAY_RESIZE_FACTOR)
                    self._lock.acquire()
                    self._image = nparr
                    self._lock.release()

if __name__ == "__main__":
    stream_cv2 = False
    
    # Get the callback function
    my_callback = CMyCallback()
    if stream_cv2 == True:
        callback_func = my_callback.datastream_callback_cv2
    else:
        callback_func = my_callback.datastream_callback
    
    try:
        st.initialize()
        st_system = st.create_system()
        st_device = st_system.create_first_device()
        
        print_info(device=st_device)
        
        # Create a datastream object for handling image stream data
        st_datastream = st_device.create_datastream()
        
        # Register callback for datastream
        callback = st_datastream.register_callback(callback_func)
        
        st_datastream.start_acquisition()
        st_device.acquisition_start()
        
        
        if stream_cv2 == True:
            while True:
                image = my_callback.image
                if image is not None:
                    cv2.imshow(winname='image', mat=image)
                key = cv2.waitKey(delay=1)
                if key != -1:
                    break
        else:
            input("Press enter to terminate\n")
        
        st_device.acquisition_stop()
        st_datastream.stop_acquisition()
    
    except Exception as exception:
        print(exception)