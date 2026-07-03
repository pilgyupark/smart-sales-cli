import unittest
import tempfile
import os
import json
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.file_handler import load_data, save_data


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_load_valid_json(self):
        """정상 JSON 파일을 로드할 수 있다."""
        path = os.path.join(self.temp_dir, 'valid.json')
        expected = [{"id": "C001", "name": "테스트"}]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(expected, f, ensure_ascii=False)
        result = load_data(path)
        self.assertEqual(result, expected)

    def test_load_nonexistent_file(self):
        """존재하지 않는 파일을 로드하면 빈 리스트를 반환한다."""
        path = os.path.join(self.temp_dir, 'nonexistent.json')
        result = load_data(path)
        self.assertEqual(result, [])

    def test_load_invalid_json(self):
        """잘못된 JSON 파일을 로드하면 빈 리스트를 반환한다."""
        path = os.path.join(self.temp_dir, 'invalid.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('{invalid json}')
        result = load_data(path)
        self.assertEqual(result, [])

    def test_save_and_load(self):
        """저장한 데이터를 다시 로드하면 동일한 데이터를 반환한다."""
        path = os.path.join(self.temp_dir, 'save_test.json')
        data = [{"key": "value"}]
        save_data(path, data)
        result = load_data(path)
        self.assertEqual(result, data)

    def test_save_empty_list(self):
        """빈 리스트를 저장하고 로드할 수 있다."""
        path = os.path.join(self.temp_dir, 'empty.json')
        save_data(path, [])
        result = load_data(path)
        self.assertEqual(result, [])

    def test_save_creates_directory(self):
        """디렉토리가 없는 경로에 저장하면 자동으로 디렉토리를 생성한다."""
        path = os.path.join(self.temp_dir, 'sub', 'nested', 'test.json')
        data = [{"id": "C001"}]
        save_data(path, data)
        self.assertTrue(os.path.exists(path))
        result = load_data(path)
        self.assertEqual(result, data)


if __name__ == '__main__':
    unittest.main()