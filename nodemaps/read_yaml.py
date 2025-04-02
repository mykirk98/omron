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

if __name__ == "__main__":
    # 예시로 사용할 yaml 파일 경로
    yaml_file_path = "./nodemaps/action.yaml"
    
    # yaml 파일 읽기
    data = read_yaml(yaml_file_path)
    
    # 읽은 데이터 출력
    print(data)