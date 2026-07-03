import json
import os


def load_data(path):
    """JSON 파일을 읽어 Python 객체로 반환한다."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[오류] 파일 읽기 실패: {e}")
        return []


def save_data(path, data):
    """Python 객체를 JSON 파일로 저장한다."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"[오류] 파일 저장 실패: {e}")