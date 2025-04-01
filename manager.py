import stapipy as st
import threading
# import time
# import os
# import cv2
# import numpy as np
# from nodemaps.setting import set_enumeration
# from nodemaps.node_values import *
from camera import CameraWorker


class CameraManager:
    """
    여러 개의 카메라를 제어하고 관리할 수 있는 매니저 클래스
    """
    
    def __init__(self, num_cameras:int=2):
        """ 
        Args:
            num_cameras: 사용할 카메라 개수
        """
        # stApi 초기화
        st.initialize()
        # 카메라 시스템 생성
        self.st_system = st.create_system()
        self.camera_list = []     # 카메라 리스트
        self.cb_func_list = []   # 콜백 함수 리스트
        self.callback_list = []  # 콜백 리스트

        for i in range(num_cameras):
            cam = CameraWorker(st_system=self.st_system, camera_index=i, isColor=True)  # 카메라 스레드 생성
            self.camera_list.append(cam)
            self.cb_func_list.append(cam.datastream_callback)  # 콜백 함수 등록
            self.callback_list.append(cam.datastream.register_callback(self.cb_func_list[i]))

    def start_all_cameras(self) -> None:
        """
        모든 카메라 스레드 실행
        """
        
        for cam in self.camera_list:
            cam.start()

    def stop_all_cameras(self) -> None:
        """
        모든 카메라 종료
        """
        
        for cam in self.camera_list:
            cam.stop_acquisition()

    def trigger_camera(self, camera_index:int, action:int) -> None:
        """
        특정 카메라 트리거
        """
        
        if 0 <= camera_index < len(self.camera_list):
            self.camera_list[camera_index].trigger(action=action)
        else:
            print("Invalid camera index. Please enter a valid index.")

    def run(self) -> None:
        """
        사용자 입력을 받아 원하는 카메라 트리거
        """
        
        # 모든 카메라 시작
        self.start_all_cameras()
        counter = 0
        while True:
            counter += 1
            
            selection = input("\nEnter camera index to trigger (or 'q' to quit):\n")

            if selection.lower() == 'q':        # 종료
                break
            elif len(selection.split()) > 1:    # 여러 카메라 트리거
                for index in selection.split():
                    if index.isdigit():
                        self.trigger_camera(camera_index=int(index), action=counter)
                    else:
                        print(f"Invalid input '{index}'. Please enter a valid camera index.")
            elif selection.isdigit():           # 단일 카메라 트리거
                self.trigger_camera(camera_index=int(selection), action=counter)
            else:                               # 잘못된 입력 처리
                print("Invalid input. Please enter a camera index or 'q'.")
        # 모든 카메라 종료
        self.stop_all_cameras()


if __name__ == "__main__":
    manager = CameraManager(num_cameras=4)  # 카메라 개수 설정
    manager.run()
