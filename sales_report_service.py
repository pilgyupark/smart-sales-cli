import json
import os

from validators import validate_required, validate_date
import customer_service

REPORT_FILE = "data/sales_reports.json"


def _load_reports():
    """영업일지 데이터를 JSON 파일에서 로드한다."""
    if not os.path.exists(REPORT_FILE):
        return []
    try:
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_reports(reports):
    """영업일지 데이터를 JSON 파일에 저장한다."""
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)


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


def register_report(customer_id, activity_date, content):
    """새 영업일지를 등록한다.

    Returns:
        (True, 등록된 report dict) 또는 (False, 오류 메시지)
    """
    # 입력 검증
    err = validate_required(customer_id, "고객사 ID")
    if err:
        return False, err

    # 고객사 존재 확인
    customer = customer_service.get_customer(customer_id.strip())
    if customer is None:
        return False, "[오류] 존재하지 않는 고객사 ID입니다."

    err = validate_date(activity_date)
    if err:
        return False, err
    err = validate_required(content, "영업 내용")
    if err:
        return False, err

    reports = _load_reports()

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
    _save_reports(reports)
    return True, report


def list_reports():
    """전체 영업일지 목록을 반환한다."""
    return _load_reports()


def update_report(report_id, activity_date, content):
    """영업일지를 수정한다. (APPROVED 상태는 수정 불가)

    Returns:
        (True, 수정된 report dict) 또는 (False, 오류 메시지)
    """
    reports = _load_reports()

    target = None
    for r in reports:
        if r.get("report_id") == report_id:
            target = r
            break

    if target is None:
        return False, "[오류] 존재하지 않는 영업일지 ID입니다."

    if target.get("status") == "APPROVED":
        return False, "[오류] APPROVED 상태인 영업일지는 수정할 수 없습니다."

    err = validate_date(activity_date)
    if err:
        return False, err
    err = validate_required(content, "영업 내용")
    if err:
        return False, err

    target["activity_date"] = activity_date.strip()
    target["content"] = content.strip()
    _save_reports(reports)
    return True, target