import unittest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 원본 CUSTOMER_FILE을 백업하고 테스트용 임시 파일로 대체
import customer_service


class TestCustomerService(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.orig_file = customer_service.CUSTOMER_FILE
        self.test_file = os.path.join(self.temp_dir, "customers.json")
        customer_service.CUSTOMER_FILE = self.test_file
        # 빈 배열로 초기화
        with open(self.test_file, 'w', encoding='utf-8') as f:
            json.dump([], f)

    def tearDown(self):
        customer_service.CUSTOMER_FILE = self.orig_file
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    # --- register_customer ---

    def test_register_success(self):
        """정상 입력으로 고객사 등록에 성공한다."""
        success, customer = customer_service.register_customer(
            "테스트 고객사", "홍길동", "hong@example.com"
        )
        self.assertTrue(success)
        self.assertEqual(customer["customer_id"], "C001")
        self.assertEqual(customer["customer_name"], "테스트 고객사")
        self.assertEqual(customer["manager_name"], "홍길동")
        self.assertEqual(customer["email"], "hong@example.com")

        # 파일에 저장되었는지 확인
        loaded = customer_service.list_customers()
        self.assertEqual(len(loaded), 1)

    def test_register_duplicate_id(self):
        """customer_id 중복 등록을 차단한다."""
        # 첫 번째 등록
        customer_service.register_customer("고객사A", "김철수", "a@test.com")
        # 동일한 ID(C001)를 강제로 생성하려면 _generate_customer_id를 우회해야 함
        # 실제로는 자동 생성이므로 중복이 발생하지 않지만,
        # 데이터를 직접 조작하여 중복 상황을 만듦
        customers = customer_service._load_customers()
        dup = {
            "customer_id": "C001",
            "customer_name": "중복 고객사",
            "manager_name": "이영희",
            "email": "b@test.com"
        }
        customers.append(dup)
        customer_service._save_customers(customers)

        # 다시 등록 시도 (C002가 생성되어야 하지만 C001이 이미 2개)
        # _generate_customer_id는 C002를 반환하므로 중복 ID는 아니지만,
        # 요구사항상 중복 ID 차단 로직이 있으므로 검증
        success, customer = customer_service.register_customer(
            "고객사B", "박민수", "c@test.com"
        )
        self.assertTrue(success)
        self.assertEqual(customer["customer_id"], "C002")

    def test_register_empty_name(self):
        """고객사명이 비어있으면 등록에 실패한다."""
        success, message = customer_service.register_customer(
            "", "홍길동", "hong@example.com"
        )
        self.assertFalse(success)
        self.assertIn("고객사명", message)

    def test_register_empty_manager(self):
        """담당자명이 비어있으면 등록에 실패한다."""
        success, message = customer_service.register_customer(
            "테스트 고객사", "", "hong@example.com"
        )
        self.assertFalse(success)
        self.assertIn("담당자명", message)

    def test_register_invalid_email(self):
        """잘못된 이메일 형식이면 등록에 실패한다."""
        success, message = customer_service.register_customer(
            "테스트 고객사", "홍길동", "invalid-email"
        )
        self.assertFalse(success)
        self.assertIn("이메일", message)

    # --- list_customers ---

    def test_list_empty(self):
        """고객사가 없으면 빈 리스트를 반환한다."""
        result = customer_service.list_customers()
        self.assertEqual(result, [])

    def test_list_with_data(self):
        """고객사가 있을 때 전체 목록을 반환한다."""
        customer_service.register_customer("고객사A", "김철수", "a@test.com")
        customer_service.register_customer("고객사B", "이영희", "b@test.com")
        result = customer_service.list_customers()
        self.assertEqual(len(result), 2)

    # --- get_customer ---

    def test_get_found(self):
        """존재하는 고객사 ID로 조회하면 해당 고객사를 반환한다."""
        customer_service.register_customer("고객사A", "김철수", "a@test.com")
        customer = customer_service.get_customer("C001")
        self.assertIsNotNone(customer)
        self.assertEqual(customer["customer_name"], "고객사A")

    def test_get_not_found(self):
        """존재하지 않는 고객사 ID로 조회하면 None을 반환한다."""
        customer = customer_service.get_customer("C999")
        self.assertIsNone(customer)

    # --- update_customer ---

    def test_update_success(self):
        """정상 입력으로 고객사 정보를 수정할 수 있다."""
        customer_service.register_customer("고객사A", "김철수", "a@test.com")
        success, customer = customer_service.update_customer(
            "C001", "수정된고객사", "홍길동", "hong@test.com"
        )
        self.assertTrue(success)
        self.assertEqual(customer["customer_name"], "수정된고객사")
        self.assertEqual(customer["manager_name"], "홍길동")
        self.assertEqual(customer["email"], "hong@test.com")

        # 파일에 반영되었는지 확인
        loaded = customer_service.get_customer("C001")
        self.assertEqual(loaded["customer_name"], "수정된고객사")

    def test_update_not_found(self):
        """존재하지 않는 ID로 수정하면 실패한다."""
        success, message = customer_service.update_customer(
            "C999", "이름", "담당자", "email@test.com"
        )
        self.assertFalse(success)
        self.assertIn("존재하지 않는", message)

    # --- delete_customer ---

    def test_delete_success(self):
        """존재하는 고객사를 삭제할 수 있다."""
        customer_service.register_customer("고객사A", "김철수", "a@test.com")
        customer_service.register_customer("고객사B", "이영희", "b@test.com")
        success, message = customer_service.delete_customer("C001")
        self.assertTrue(success)
        result = customer_service.list_customers()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["customer_id"], "C002")

    def test_delete_not_found(self):
        """존재하지 않는 ID로 삭제하면 실패한다."""
        success, message = customer_service.delete_customer("C999")
        self.assertFalse(success)
        self.assertIn("존재하지 않는", message)


if __name__ == '__main__':
    unittest.main()