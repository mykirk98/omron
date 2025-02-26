import stapipy as st


class CMyCallback:
    """
    Class that contains a callback function
    """
    # def __init__(self):
    #     self._image = None
    #     self._lock = threading.Lock()

    def datastream_callback(self, handle=None, context=None):
        """
        Callback to handle events from DataStream
        
        handle : handle that trigger the callback
        context : user data passed on during callback registration
        """
        
        st_datastream = handle.module
        if st_datastream:
            with st_datastream.retrieve_buffer() as st_buffer:
                # Check if the acquired data contains image data
                if st_buffer.info.is_image_present == True:
                    # Create an image object
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