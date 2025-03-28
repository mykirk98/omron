import stapipy as st

def set_enumeration(nodemap, enum_name, entry_name):
    """
    열거형 노드의 값을 설정하는 함수
    
    Args:
        nodemap: 카메라 설정을 위한 노드 맵
        enum_name: 열거형 노드의 값
        entry_name: 열거형 엔트리 노드의 값
    """
    
    # 열거형 노드 가져오기
    enum_node = st.PyIEnumeration(nodemap.get_node(enum_name))
    # 열거형 엔트리 노드 가져오기
    entry_node = st.PyIEnumEntry(enum_node[entry_name])
    # 열거형 노드의 값 설정
    enum_node.set_entry_value(entry_node)