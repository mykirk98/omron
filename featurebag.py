import os
import tempfile
import stapipy as st

try:
    st.initialize()
    
    # 시스템 생성 및 카메라 연결
    st_system = st.create_system()
    st_device = st_system.create_first_device()
    print(f"device : {st_device.info.display_name}")
    
    # 설정을 저장할 파일 경로 지정
    filename = os.path.join(os.curdir, "features.cfg")
    
    nodemap = st_device.remote_port.nodemap
    featurebag = st.create_featurebag()
    
    featurebag.store_nodemap_to_bag(nodemap)
    
    features = featurebag.save_to_string()
    print(features)
    
    print(f"Saving features to file: {filename}")
    featurebag.save_to_file(filename)
    print(f"Features saved to file: {filename}")
    
    # featurebag.clear()
    # print("Featurebag cleared")
    
    featurebag2 = st.create_featurebag()
    # featurebag2.store_nodemap_from_file(filename)
    featurebag2.store_file_to_bag(filename)
    
    print("Loading features to camera")
    featurebag2.load(nodemap, True)
    print("Loading to camera complete")
    
except Exception as exception:
    print(f"An exception occurred: {exception}")