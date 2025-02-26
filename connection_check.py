import stapipy as st

def datastream_callback(handle=None, context=None):
    """
    Callback to handle events from DataStream
    
    handle : handle that trigger the callback
    context : user data passed on during callback registration
    """
    
    st_datastream = handle.module
    if st_datastream:
        with st_datastream.retrieve_buffer() as st_buffer:
            if st_buffer.info.is_image_present == True:
                st_image = st_buffer.get_image()
                print(f"BlockID : {st_buffer.info.frame_id} Size : {st_image.width} x {st_image.height} First Byte : {st_image.get_image_data()[0]}")
                # print(f"BlockID : {st_buffer.info.frame_id} Size : {st_image.shape} First Byte : {st_image.get_image_data()[0]}")
                # print(f"BlockID : {st_buffer.info.frame_id} Size : {st_image.shape} Byte : {st_image.get_image_data()}")
            else:
                # print("Image data does'nt exist")
                print("Image data does not exist")


if __name__ == "__main__":
    try:
        st.initialize()
        st_system = st.create_system()
        st_device = st_system.create_first_device()
        
        print(f"device : {st_device.info.display_name}")
        
        # Create a datastream object for handling image stream data
        st_datastream = st_device.create_datastream()
        
        callback = st_datastream.register_callback(datastream_callback)
        
        st_datastream.start_acquisition()
        st_device.acquisition_start()
        
        input("Press enter to terminate")
        
        st_device.acquisition_stop()
        st_datastream.stop_acquisition()
    
    except Exception as exception:
        print(exception)