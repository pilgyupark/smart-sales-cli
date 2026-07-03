import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.report import (
    register_report,
    list_reports,
    update_report,
    submit_report,
    approve_report,
    reject_report,
    withdraw_report,
)


class TestRegisterReport(unittest.TestCase):

    def setUp(self):
        self.reports = []
        self.customers = [
            {"customer_id": "C001", "customer_name": "테스트 고객사",
             "manager_name": "홍길동", "email": "hong@example.com"},
        ]

    def test_register_success(self):
        """정상 입력으로 영업일지 등록에 성공한다."""
        success, report = register_report(
            self.reports, self.customers, "C001", "2026-06-09", "제품 소개 미팅"
        )
        self.assertTrue(success)
        self.assertEqual(report["report_id"], "R001")
        self.assertEqual(report["customer_id"], "C001")
        self.assertEqual(report["activity_date"], "2026-06-09")
        self.assertEqual(report["content"], "제품 소개 미팅")
        self.assertEqual(report["status"], "DRAFT")
        self.assertEqual(len(self.reports), 1)

    def test_register_empty_customer_id(self):
        """고객사 ID가 비어있으면 등록에 실패한다."""
        success, message = register_report(
            self.reports, self.customers, "", "2026-06-09", "미팅"
        )
        self.assertFalse(success)
        self.assertEqual(len(self.reports), 0)

    def test_register_invalid_customer_id_format(self):
        """잘못된 형식의 고객사 ID면 등록에 실패한다."""
        success, message = register_report(
            self.reports, self.customers, "X001", "2026-06-09", "미팅"
        )
        self.assertFalse(success)
        self.assertIn("고객사 ID 형식", message)
        self.assertEqual(len(self.reports), 0)

    def test_register_nonexistent_customer(self):
        """존재하지 않는 고객사 ID면 등록에 실패한다."""
        success, message = register_report(
            self.reports, self.customers, "C999", "2026-06-09", "미팅"
        )
        self.assertFalse(success)
        self.assertIn("존재하지 않는 고객사", message)
        self.assertEqual(len(self.reports), 0)

    def test_register_invalid_date(self):
        """잘못된 날짜 형식이면 등록에 실패한다."""
        success, message = register_report(
            self.reports, self.customers, "C001", "26-06-09", "미팅"
        )
        self.assertFalse(success)
        self.assertIn("날짜", message)
        self.assertEqual(len(self.reports), 0)

    def test_register_empty_content(self):
        """영업 내용이 비어있으면 등록에 실패한다."""
        success, message = register_report(
            self.reports, self.customers, "C001", "2026-06-09", ""
        )
        self.assertFalse(success)
        self.assertIn("영업 내용", message)
        self.assertEqual(len(self.reports), 0)

    def test_register_auto_increment_id(self):
        """연속 등록 시 ID가 자동으로 증가한다."""
        register_report(self.reports, self.customers, "C001", "2026-06-01", "미팅1")
        register_report(self.reports, self.customers, "C001", "2026-06-02", "미팅2")
        register_report(self.reports, self.customers, "C001", "2026-06-03", "미팅3")

        self.assertEqual(len(self.reports), 3)
        self.assertEqual(self.reports[0]["report_id"], "R001")
        self.assertEqual(self.reports[1]["report_id"], "R002")
        self.assertEqual(self.reports[2]["report_id"], "R003")


class TestListReports(unittest.TestCase):

    def test_list_empty(self):
        """빈 리스트를 전달하면 빈 리스트를 반환한다."""
        result = list_reports([])
        self.assertEqual(result, [])

    def test_list_with_data(self):
        """데이터가 있을 때 전체 목록을 반환한다."""
        reports = [
            {"report_id": "R001", "customer_id": "C001",
             "activity_date": "2026-06-01", "content": "미팅1", "status": "DRAFT"},
            {"report_id": "R002", "customer_id": "C002",
             "activity_date": "2026-06-02", "content": "미팅2", "status": "DRAFT"},
        ]
        result = list_reports(reports)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["report_id"], "R001")
        self.assertEqual(result[1]["report_id"], "R002")


class TestUpdateReport(unittest.TestCase):

    def setUp(self):
        self.reports = [
            {"report_id": "R001", "customer_id": "C001",
             "activity_date": "2026-06-01", "content": "원본 내용", "status": "DRAFT"},
            {"report_id": "R002", "customer_id": "C001",
             "activity_date": "2026-06-02", "content": "제출된 내용", "status": "SUBMITTED"},
        ]

    def test_update_success(self):
        """DRAFT 상태의 영업일지를 수정할 수 있다."""
        success, report = update_report(
            self.reports, "R001", "2026-06-15", "수정된 내용"
        )
        self.assertTrue(success)
        self.assertEqual(report["activity_date"], "2026-06-15")
        self.assertEqual(report["content"], "수정된 내용")
        self.assertEqual(report["status"], "DRAFT")

    def test_update_not_found(self):
        """존재하지 않는 ID로 수정하면 실패한다."""
        success, message = update_report(
            self.reports, "R999", "2026-06-15", "내용"
        )
        self.assertFalse(success)
        self.assertIn("존재하지 않는", message)

    def test_update_not_draft(self):
        """DRAFT 상태가 아닌 영업일지는 수정할 수 없다."""
        success, message = update_report(
            self.reports, "R002", "2026-06-15", "수정 시도"
        )
        self.assertFalse(success)
        self.assertIn("DRAFT 상태에서만", message)
        self.assertEqual(self.reports[1]["content"], "제출된 내용")


class TestStatusTransition(unittest.TestCase):

    def setUp(self):
        self.reports = [
            {"report_id": "R001", "customer_id": "C001",
             "activity_date": "2026-06-01", "content": "초안", "status": "DRAFT"},
            {"report_id": "R002", "customer_id": "C001",
             "activity_date": "2026-06-02", "content": "제출됨", "status": "SUBMITTED"},
            {"report_id": "R003", "customer_id": "C001",
             "activity_date": "2026-06-03", "content": "승인됨", "status": "APPROVED"},
        ]

    def test_submit_success(self):
        """DRAFT 상태에서 상신하면 SUBMITTED가 된다."""
        success, message = submit_report(self.reports, "R001")
        self.assertTrue(success)
        self.assertEqual(self.reports[0]["status"], "SUBMITTED")

    def test_approve_success(self):
        """SUBMITTED 상태에서 승인하면 APPROVED가 된다."""
        success, message = approve_report(self.reports, "R002")
        self.assertTrue(success)
        self.assertEqual(self.reports[1]["status"], "APPROVED")

    def test_reject_success(self):
        """SUBMITTED 상태에서 반려하면 REJECTED가 된다."""
        success, message = reject_report(self.reports, "R002")
        self.assertTrue(success)
        self.assertEqual(self.reports[1]["status"], "REJECTED")

    def test_withdraw_success(self):
        """SUBMITTED 상태에서 회수하면 DRAFT가 된다."""
        success, message = withdraw_report(self.reports, "R002")
        self.assertTrue(success)
        self.assertEqual(self.reports[1]["status"], "DRAFT")

    def test_submit_not_draft(self):
        """SUBMITTED 상태에서 상신하면 실패한다."""
        success, message = submit_report(self.reports, "R002")
        self.assertFalse(success)
        self.assertIn("DRAFT 상태에서만", message)

    def test_approve_not_submitted(self):
        """DRAFT 상태에서 승인하면 실패한다."""
        success, message = approve_report(self.reports, "R001")
        self.assertFalse(success)
        self.assertIn("SUBMITTED 상태에서만", message)

    def test_reject_not_submitted(self):
        """DRAFT 상태에서 반려하면 실패한다."""
        success, message = reject_report(self.reports, "R001")
        self.assertFalse(success)
        self.assertIn("SUBMITTED 상태에서만", message)

    def test_withdraw_not_submitted(self):
        """DRAFT 상태에서 회수하면 실패한다."""
        success, message = withdraw_report(self.reports, "R001")
        self.assertFalse(success)
        self.assertIn("SUBMITTED 상태에서만", message)

    def test_approve_already_approved(self):
        """APPROVED 상태에서 승인하면 실패한다."""
        success, message = approve_report(self.reports, "R003")
        self.assertFalse(success)
        self.assertIn("SUBMITTED 상태에서만", message)

    def test_transition_not_found(self):
        """존재하지 않는 ID로 상태 전이를 시도하면 실패한다."""
        success, message = submit_report(self.reports, "R999")
        self.assertFalse(success)
        self.assertIn("존재하지 않는", message)


if __name__ == '__main__':
    unittest.main()
