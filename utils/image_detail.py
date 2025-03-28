from PIL import Image
import numpy as np


def show_detail_info(path: str) -> None:
    """
    show image detail information
    
    Args:
        path: image path
    """
    
    img = Image.open(fp=path)
    img_arr = np.array(object=img)
    
    print(f"Image path: {path}")
    print(f"Image shape: {img_arr.shape}")
    print(f"Image dtype: {img_arr.dtype}")
    print(f"Image len: {img_arr.__len__()}")
    print(f"Image size: {img_arr.size}")    # width * height * (channel)
    print(f"Image ndim: {img_arr.ndim}")    # 차원수 (2차원: 흑백, 3차원: 컬러)
    print(f"Image nbytes: {img_arr.nbytes}")
    print(f"Image sizeof: {img_arr.__sizeof__()}")  # width * height + 메타데이터