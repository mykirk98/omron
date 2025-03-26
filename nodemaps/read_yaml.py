import yaml

def read_yaml(file_path):
    """
    yaml 파일을 읽어서 딕셔너리로 반환하는 함수

    Args:
        yaml_fp: yaml 파일 경로

    Returns:
        data: yaml 파일을 읽어서 반환된 딕셔너리
    """
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
        return data