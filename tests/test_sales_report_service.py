import unittest
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import sales_report_service
import customer_service


class TestSalesReportService(unittest.TestCase):

    def setUp(self):
        # 임시 디렉토리 생성
        self.temp_dir = tempfile.mkdtemp()

        # sales_report_service의 REPORT_FILE을 임시 파일로 변경
        self.orig_report_file = sales_report_service.REPORT_FILE
        self.test_report_file = os.path.join(self.temp_dir, "sales_reports.json")
        sales_report_service.REPORT_FILE = self.test_report_file
        with open(self.test_report_file, 'w', encoding='utf-8') as f:
            json.dump([], f)

        # customer_service의 CUSTOMER_FILE을 임시 파일로 변경
        self.orig_customer_file = customer_service.CUSTOMER_FILE
        self.test_customer_file = os.path.join(self.temp_dir, "customers.json")
        customer_service.CUSTOMER_FILE = self.test_customer_file
        with open(self.test_customer_file, 'w', encoding='utf-8') as f:
            json.dump([], f)

        # 테스트용 고객사 데이터 준비
        customer_service.register_customer("테스트 고객사", "홍길동", "hong@example.com")
        customer_service.register_customer("두번째 고객사", "김철수", "kim@example.com")

    def tearDown(self):
        sales_report_service.REPORT_FILE = self.orig_report_file
        customer_service.CUSTOMER_FILE = self.orig_customer_file
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    # --- register_report ---

    def test_register_success(self):
        """정상 입력으로 영업일지 등록에 성공한다."""
        success, report = sales_report_service.register_report(
            "C001", "2026-06-09", "제품 소개 미팅"
        )
        self.assertTrue(success)
        self.assertEqual(report["report_id"], "R001")
        self.assertEqual(report["customer_id"], "C001")
        self.assertEqual(report["activity_date"], "2026-06-09")
        self.assertEqual(report["content"], "제품 소개 미팅")
        self.assertEqual(report["status"], "DRAFT")

        # 파일에 저장되었는지 확인
        loaded = sales_report_service.list_reports()
        self.assertEqual(len(loaded), 1)

    def test_register_nonexistent_customer(self):
        """존재하지 않는 고객사 ID면 등록에 실패한다."""
        success, message = sales_report_service.register_report(
            "C999", "2026-06-09", "미팅"
        )
        self.assertFalse(success)
        self.assertIn("존재하지 않는 고객사", message)
        self.assertEqual(len(sales_report_service.list_reports()), 0)

    def test_register_empty_customer_id(self):
        """고객사 ID가 비어있으면 등록에 실패한다."""
        success, message = sales_report_service.register_report(
            "", "2026-06-09", "미팅"
        )
        self.assertFalse(success)
        self.assertEqual(len(sales_report_service.list_reports()), 0)

    def test_register_invalid_date(self):
        """잘못된 날짜 형식이면 등록에 실패한다."""
        success, message = sales_report_service.register_report(
            "C001", "26-06-09", "미팅"
        )
        self.assertFalse(success)
        self.assertIn("날짜", message)
        self.assertEqual(len(sales_report_service.list_reports()), 0)

    def test_register_empty_content(self):
        """영업 내용이 비어있으면 등록에 실패한다."""
        success, message = sales_report_service.register_report(
            "C001", "2026-06-09", ""
        )
        self.assertFalse(success)
        self.assertIn("영업 내용", message)
        self.assertEqual(len(sales_report_service.list_reports()), 0)

    def test_register_auto_increment_id(self):
        """연속 등록 시 ID가 자동으로 증가한다."""
        sales_report_service.register_report("C001", "2026-06-01", "미팅1")
        sales_report_service.register_report("C001", "2026-06-02", "미팅2")
        sales_report_service.register_report("C002", "2026-06-03", "미팅3")

        reports = sales_report_service.list_reports()
        self.assertEqual(len(reports), 3)
        self.assertEqual(reports[0]["report_id"], "R001")
        self.assertEqual(reports[1]["report_id"], "R002")
        self.assertEqual(reports[2]["report_id"], "R003")

    # --- list_reports ---

    def test_list_empty(self):
        """영업일지가 없으면 빈 리스트를 반환한다."""
        result = sales_report_service.list_reports()
        self.assertEqual(result, [])

    def test_list_with_data(self):
        """영업일지가 있을 때 전체 목록을 반환한다."""
        sales_report_service.register_report("C001", "2026-06-01", "미팅1")
        sales_report_service.register_report("C002", "2026-06-02", "미팅2")
        result = sales_report_service.list_reports()
        self.assertEqual(len(result), 2)

    # --- update_report ---

    def test_update_success(self):
        """DRAFT 상태의 영업일지를 수정할 수 있다."""
        sales_report_service.register_report("C001", "2026-06-01", "원본 내용")
        success, report = sales_report_service.update_report(
            "R001", "2026-06-15", "수정된 내용"
        )
        self.assertTrue(success)
        self.assertEqual(report["activity_date"], "2026-06-15")
        self.assertEqual(report["content"], "수정된 내용")

        # 파일에 반영되었는지 확인
        loaded = sales_report_service.list_reports()
        self.assertEqual(loaded[0]["content"], "수정된 내용")

    def test_update_approved_blocked(self):
        """APPROVED 상태인 영업일지는 수정할 수 없다."""
        # APPROVED 상태의 영업일지를 직접 생성
        reports = sales_report_service._load_reports()
        approved_report = {
            "report_id": "R001",
            "customer_id": "C001",
            "activity_date": "2026-06-01",
            "content": "승인된 보고서",
            "status": "APPROVED"
        }
        reports.append(approved_report)
        sales_report_service._save_reports(reports)

        success, message = sales_report_service.update_report(
            "R001", "2026-06-15", "수정 시도"
        )
        self.assertFalse(success)
        self.assertIn("APPROVED", message)

    def test_update_not_found(self):
        """존재하지 않는 ID로 수정하면 실패한다."""
        success, message = sales_report_service.update_report(
            "R999", "2026-06-15", "내용"
        )
        self.assertFalse(success)
        self.assertIn("존재하지 않는", message)


if __name__ == '__main__':
    unittest.main()