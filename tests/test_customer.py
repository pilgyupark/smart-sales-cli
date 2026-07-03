import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.customer import (
    register_customer,
    list_customers,
    get_customer,
    search_customers,
    update_customer,
    delete_customer,
)


class TestRegisterCustomer(unittest.TestCase):

    def setUp(self):
        self.customers = []

    def test_register_success(self):
        """정상 입력으로 고객사 등록에 성공한다."""
        success, customer = register_customer(
            self.customers, "테스트 고객사", "홍길동", "hong@example.com"
        )
        self.assertTrue(success)
        self.assertEqual(customer["customer_id"], "C001")
        self.assertEqual(customer["customer_name"], "테스트 고객사")
        self.assertEqual(customer["manager_name"], "홍길동")
        self.assertEqual(customer["email"], "hong@example.com")
        self.assertEqual(len(self.customers), 1)

    def test_register_empty_name(self):
        """고객사명이 비어있으면 등록에 실패한다."""
        success, message = register_customer(
            self.customers, "", "홍길동", "hong@example.com"
        )
        self.assertFalse(success)
        self.assertIn("고객사명", message)
        self.assertEqual(len(self.customers), 0)

    def test_register_empty_manager(self):
        """담당자명이 비어있으면 등록에 실패한다."""
        success, message = register_customer(
            self.customers, "테스트 고객사", "", "hong@example.com"
        )
        self.assertFalse(success)
        self.assertIn("담당자명", message)
        self.assertEqual(len(self.customers), 0)

    def test_register_invalid_email(self):
        """잘못된 이메일 형식이면 등록에 실패한다."""
        success, message = register_customer(
            self.customers, "테스트 고객사", "홍길동", "invalid-email"
        )
        self.assertFalse(success)
        self.assertIn("이메일", message)
        self.assertEqual(len(self.customers), 0)

    def test_register_whitespace_name(self):
        """고객사명이 공백만 있으면 등록에 실패한다."""
        success, message = register_customer(
            self.customers, "   ", "홍길동", "hong@example.com"
        )
        self.assertFalse(success)
        self.assertIn("고객사명", message)
        self.assertEqual(len(self.customers), 0)

    def test_register_auto_increment_id(self):
        """연속 등록 시 ID가 자동으로 증가한다."""
        register_customer(self.customers, "고객사A", "김철수", "a@test.com")
        register_customer(self.customers, "고객사B", "이영희", "b@test.com")
        register_customer(self.customers, "고객사C", "박민수", "c@test.com")

        self.assertEqual(len(self.customers), 3)
        self.assertEqual(self.customers[0]["customer_id"], "C001")
        self.assertEqual(self.customers[1]["customer_id"], "C002")
        self.assertEqual(self.customers[2]["customer_id"], "C003")


class TestListCustomers(unittest.TestCase):

    def test_list_empty(self):
        """빈 리스트를 전달하면 빈 리스트를 반환한다."""
        result = list_customers([])
        self.assertEqual(result, [])

    def test_list_with_data(self):
        """데이터가 있을 때 전체 목록을 반환한다."""
        customers = [
            {"customer_id": "C001", "customer_name": "고객사A",
             "manager_name": "김철수", "email": "a@test.com"},
            {"customer_id": "C002", "customer_name": "고객사B",
             "manager_name": "이영희", "email": "b@test.com"},
        ]
        result = list_customers(customers)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["customer_id"], "C001")
        self.assertEqual(result[1]["customer_id"], "C002")


class TestGetCustomer(unittest.TestCase):

    def setUp(self):
        self.customers = [
            {"customer_id": "C001", "customer_name": "고객사A",
             "manager_name": "김철수", "email": "a@test.com"},
            {"customer_id": "C002", "customer_name": "고객사B",
             "manager_name": "이영희", "email": "b@test.com"},
        ]

    def test_get_customer_found(self):
        """존재하는 고객사 ID로 조회하면 해당 고객사를 반환한다."""
        result = get_customer(self.customers, "C001")
        self.assertIsNotNone(result)
        self.assertEqual(result["customer_name"], "고객사A")

    def test_get_customer_not_found(self):
        """존재하지 않는 고객사 ID로 조회하면 None을 반환한다."""
        result = get_customer(self.customers, "C999")
        self.assertIsNone(result)


class TestSearchCustomers(unittest.TestCase):

    def setUp(self):
        self.customers = [
            {"customer_id": "C001", "customer_name": "삼성전자",
             "manager_name": "김철수", "email": "kim@test.com"},
            {"customer_id": "C002", "customer_name": "LG전자",
             "manager_name": "이영희", "email": "lee@test.com"},
            {"customer_id": "C003", "customer_name": "SK하이닉스",
             "manager_name": "박민수", "email": "park@test.com"},
        ]

    def test_search_by_name(self):
        """고객사명으로 부분 검색할 수 있다."""
        results = search_customers(self.customers, "전자")
        self.assertEqual(len(results), 2)
        self.assertIn("삼성전자", [r["customer_name"] for r in results])
        self.assertIn("LG전자", [r["customer_name"] for r in results])

    def test_search_by_manager(self):
        """담당자명으로 부분 검색할 수 있다."""
        results = search_customers(self.customers, "김")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["customer_name"], "삼성전자")

    def test_search_no_result(self):
        """검색 결과가 없으면 빈 리스트를 반환한다."""
        results = search_customers(self.customers, "없는회사")
        self.assertEqual(results, [])

    def test_search_empty_keyword(self):
        """키워드가 비어있으면 전체 목록을 반환한다."""
        results = search_customers(self.customers, "")
        self.assertEqual(len(results), 3)


class TestUpdateCustomer(unittest.TestCase):

    def setUp(self):
        self.customers = [
            {"customer_id": "C001", "customer_name": "고객사A",
             "manager_name": "김철수", "email": "a@test.com"},
        ]

    def test_update_success(self):
        """정상 입력으로 고객사 정보를 수정할 수 있다."""
        success, customer = update_customer(
            self.customers, "C001", "수정된고객사", "홍길동", "hong@test.com"
        )
        self.assertTrue(success)
        self.assertEqual(customer["customer_name"], "수정된고객사")
        self.assertEqual(customer["manager_name"], "홍길동")
        self.assertEqual(customer["email"], "hong@test.com")

    def test_update_not_found(self):
        """존재하지 않는 ID로 수정하면 실패한다."""
        success, message = update_customer(
            self.customers, "C999", "이름", "담당자", "email@test.com"
        )
        self.assertFalse(success)
        self.assertIn("존재하지 않는", message)

    def test_update_invalid_email(self):
        """잘못된 이메일로 수정하면 실패한다."""
        success, message = update_customer(
            self.customers, "C001", "이름", "담당자", "invalid"
        )
        self.assertFalse(success)
        self.assertIn("이메일", message)


class TestDeleteCustomer(unittest.TestCase):

    def setUp(self):
        self.customers = [
            {"customer_id": "C001", "customer_name": "고객사A",
             "manager_name": "김철수", "email": "a@test.com"},
            {"customer_id": "C002", "customer_name": "고객사B",
             "manager_name": "이영희", "email": "b@test.com"},
        ]

    def test_delete_success(self):
        """존재하는 고객사를 삭제할 수 있다."""
        success, message = delete_customer(self.customers, "C001")
        self.assertTrue(success)
        self.assertEqual(len(self.customers), 1)
        self.assertEqual(self.customers[0]["customer_id"], "C002")

    def test_delete_not_found(self):
        """존재하지 않는 ID로 삭제하면 실패한다."""
        success, message = delete_customer(self.customers, "C999")
        self.assertFalse(success)
        self.assertIn("존재하지 않는", message)
        self.assertEqual(len(self.customers), 2)


if __name__ == '__main__':
    unittest.main()
