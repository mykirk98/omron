import stapipy as st
# import logging

class Camera:
    def __init__(self, st_system):
        # self.device = self.st_system.create_first_device()
        self.device = st_system.create_first_device()
        self.datastream = self.device.create_datastream()
    
    def start(self):
        self.datastream.start_acquisition()
        self.device.acquisition_start()
        print(f"Device {self.device.info.display_name} started")
    
    def stop(self):
        self.device.acquisition_stop()
        self.datastream.stop_acquisition()
        print(f"Device {self.device.info.display_name} stopped")


if __name__ == "__main__":
    st.initialize()
    st_system = st.create_system()
    
    cam1 = Camera(st_system=st_system)
    cam1.start()
    cam1.stop()