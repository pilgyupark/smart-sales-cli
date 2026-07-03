import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.validator import (
    validate_required,
    validate_email,
    validate_date,
    validate_customer_id,
    validate_report_id,
)


class TestValidateRequired(unittest.TestCase):

    def test_valid_string(self):
        """정상 문자열은 None을 반환한다."""
        self.assertIsNone(validate_required("hello", "이름"))

    def test_empty_string(self):
        """빈 문자열은 오류 메시지를 반환한다."""
        result = validate_required("", "이름")
        self.assertIsNotNone(result)
        self.assertIn("필수 입력값", result)

    def test_whitespace_string(self):
        """공백 문자열은 오류 메시지를 반환한다."""
        result = validate_required("   ", "이름")
        self.assertIsNotNone(result)
        self.assertIn("필수 입력값", result)

    def test_none_value(self):
        """None은 오류 메시지를 반환한다."""
        result = validate_required(None, "이름")
        self.assertIsNotNone(result)
        self.assertIn("필수 입력값", result)


class TestValidateEmail(unittest.TestCase):

    def test_valid_email(self):
        """정상 이메일은 None을 반환한다."""
        self.assertIsNone(validate_email("hong@example.com"))

    def test_no_at_symbol(self):
        """@가 없으면 오류 메시지를 반환한다."""
        result = validate_email("hongexample.com")
        self.assertIsNotNone(result)
        self.assertIn("이메일 형식", result)

    def test_no_domain_dot(self):
        """도메인에 .이 없으면 오류 메시지를 반환한다."""
        result = validate_email("hong@example")
        self.assertIsNotNone(result)
        self.assertIn("이메일 형식", result)

    def test_short_tld(self):
        """최상위 도메인이 1자이면 오류 메시지를 반환한다."""
        result = validate_email("hong@example.c")
        self.assertIsNotNone(result)
        self.assertIn("이메일 형식", result)

    def test_empty_email(self):
        """빈 문자열은 오류 메시지를 반환한다."""
        result = validate_email("")
        self.assertIsNotNone(result)

    def test_whitespace_email(self):
        """공백 문자열은 오류 메시지를 반환한다."""
        result = validate_email("   ")
        self.assertIsNotNone(result)


class TestValidateDate(unittest.TestCase):

    def test_valid_date(self):
        """정상 날짜(YYYY-MM-DD)는 None을 반환한다."""
        self.assertIsNone(validate_date("2026-06-09"))

    def test_invalid_format(self):
        """잘못된 형식(YY-MM-DD)은 오류 메시지를 반환한다."""
        result = validate_date("26-06-09")
        self.assertIsNotNone(result)
        self.assertIn("날짜 형식", result)

    def test_invalid_date(self):
        """존재하지 않는 날짜(2월 30일)는 오류 메시지를 반환한다."""
        result = validate_date("2026-02-30")
        self.assertIsNotNone(result)
        self.assertIn("존재하지 않는 날짜", result)

    def test_empty_date(self):
        """빈 문자열은 오류 메시지를 반환한다."""
        result = validate_date("")
        self.assertIsNotNone(result)

    def test_random_string(self):
        """날짜 형식이 아닌 문자열은 오류 메시지를 반환한다."""
        result = validate_date("abc-def-gh")
        self.assertIsNotNone(result)
        self.assertIn("날짜 형식", result)

    def test_leap_year_feb29(self):
        """윤년 2월 29일은 정상으로 처리한다."""
        self.assertIsNone(validate_date("2024-02-29"))


class TestValidateCustomerId(unittest.TestCase):

    def test_valid_customer_id(self):
        """정상 고객사 ID(C001)는 None을 반환한다."""
        self.assertIsNone(validate_customer_id("C001"))

    def test_invalid_prefix(self):
        """C로 시작하지 않으면 오류 메시지를 반환한다."""
        result = validate_customer_id("X001")
        self.assertIsNotNone(result)
        self.assertIn("고객사 ID 형식", result)

    def test_too_short(self):
        """숫자가 3자리가 아니면 오류 메시지를 반환한다."""
        result = validate_customer_id("C01")
        self.assertIsNotNone(result)
        self.assertIn("고객사 ID 형식", result)

    def test_empty_id(self):
        """빈 문자열은 오류 메시지를 반환한다."""
        result = validate_customer_id("")
        self.assertIsNotNone(result)


class TestValidateReportId(unittest.TestCase):

    def test_valid_report_id(self):
        """정상 영업일지 ID(R001)는 None을 반환한다."""
        self.assertIsNone(validate_report_id("R001"))

    def test_invalid_prefix(self):
        """R로 시작하지 않으면 오류 메시지를 반환한다."""
        result = validate_report_id("X001")
        self.assertIsNotNone(result)
        self.assertIn("영업일지 ID 형식", result)

    def test_too_short(self):
        """숫자가 3자리가 아니면 오류 메시지를 반환한다."""
        result = validate_report_id("R01")
        self.assertIsNotNone(result)
        self.assertIn("영업일지 ID 형식", result)

    def test_empty_id(self):
        """빈 문자열은 오류 메시지를 반환한다."""
        result = validate_report_id("")
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()