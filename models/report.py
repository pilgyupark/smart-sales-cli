import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.validator import validate_required, validate_date, validate_customer_id
from models.customer import get_customer


def _generate_report_id(reports):
    """새 영업일지 ID를 자동 생성한다."""
    if not reports:
        return "R001"
    max_num = 0
    for r in reports:
        rid = r.get("report_id", "")
        if rid.startswith("R") and rid[1:].isdigit():
            num = int(rid[1:])
            if num > max_num:
                max_num = num
    return f"R{max_num + 1:03d}"


def register_report(reports, customers, customer_id, activity_date, content):
    """새 영업일지를 등록한다.

    Returns:
        (True, 등록된 report dict) 또는 (False, 오류 메시지)
    """
    # 입력 검증
    err = validate_required(customer_id, "고객사 ID")
    if err:
        return False, err
    err = validate_customer_id(customer_id)
    if err:
        return False, err

    # 고객사 존재 확인
    customer = get_customer(customers, customer_id.strip())
    if customer is None:
        return False, "[오류] 존재하지 않는 고객사 ID입니다."

    err = validate_date(activity_date)
    if err:
        return False, err
    err = validate_required(content, "영업 내용")
    if err:
        return False, err

    # ID 자동 생성
    report_id = _generate_report_id(reports)

    report = {
        "report_id": report_id,
        "customer_id": customer_id.strip(),
        "activity_date": activity_date.strip(),
        "content": content.strip(),
        "status": "DRAFT",
    }
    reports.append(report)
    return True, report


def list_reports(reports):
    """전체 영업일지 목록을 반환한다."""
    return list(reports)


def update_report(reports, report_id, activity_date, content):
    """영업일지를 수정한다. (DRAFT 상태에서만 가능)

    Returns:
        (True, 수정된 report dict) 또는 (False, 오류 메시지)
    """
    for report in reports:
        if report.get("report_id") == report_id:
            if report.get("status") != "DRAFT":
                return False, "[오류] DRAFT 상태에서만 수정할 수 있습니다."

            err = validate_date(activity_date)
            if err:
                return False, err
            err = validate_required(content, "영업 내용")
            if err:
                return False, err

            report["activity_date"] = activity_date.strip()
            report["content"] = content.strip()
            return True, report
    return False, "[오류] 존재하지 않는 영업일지 ID입니다."


def _transition_status(reports, report_id, required_status, new_status, action_name):
    """상태 전이를 수행하는 내부 함수."""
    for report in reports:
        if report.get("report_id") == report_id:
            if report.get("status") != required_status:
                return False, f"[오류] {required_status} 상태에서만 {action_name}할 수 있습니다."
            report["status"] = new_status
            return True, f"[{action_name} 완료] {report_id}가 {new_status} 상태로 변경되었습니다."
    return False, "[오류] 존재하지 않는 영업일지 ID입니다."


def submit_report(reports, report_id):
    """영업일지를 상신한다. (DRAFT → SUBMITTED)"""
    return _transition_status(reports, report_id, "DRAFT", "SUBMITTED", "상신")


def approve_report(reports, report_id):
    """영업일지를 승인한다. (SUBMITTED → APPROVED)"""
    return _transition_status(reports, report_id, "SUBMITTED", "APPROVED", "승인")


def reject_report(reports, report_id):
    """영업일지를 반려한다. (SUBMITTED → REJECTED)"""
    return _transition_status(reports, report_id, "SUBMITTED", "REJECTED", "반려")


def withdraw_report(reports, report_id):
    """영업일지를 회수한다. (SUBMITTED → DRAFT)"""
    return _transition_status(reports, report_id, "SUBMITTED", "DRAFT", "회수")
