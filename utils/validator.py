import re
from datetime import datetime


def validate_required(value, field_name):
    """필수 입력값이 비어있지 않은지 검증한다."""
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return f"[오류] {field_name}은(는) 필수 입력값입니다."
    return None


def validate_email(email):
    """이메일 형식을 검증한다."""
    if not email or not isinstance(email, str) or email.strip() == '':
        return "[오류] 이메일은 필수 입력값입니다."
    email = email.strip()
    if '@' not in email:
        return "[오류] 이메일 형식이 올바르지 않습니다. (@가 없습니다)"
    local_part, domain_part = email.rsplit('@', 1)
    if '.' not in domain_part:
        return "[오류] 이메일 형식이 올바르지 않습니다. (도메인에 .이 없습니다)"
    if len(domain_part.split('.')[-1]) < 2:
        return "[오류] 이메일 형식이 올바르지 않습니다. (최상위 도메인이 너무 짧습니다)"
    return None


def validate_date(date_str):
    """날짜가 YYYY-MM-DD 형식이고 실제 존재하는 날짜인지 검증한다."""
    if not date_str or not isinstance(date_str, str) or date_str.strip() == '':
        return "[오류] 날짜는 필수 입력값입니다."
    date_str = date_str.strip()
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return "[오류] 날짜 형식이 올바르지 않습니다. (YYYY-MM-DD 형식으로 입력해주세요)"
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return "[오류] 존재하지 않는 날짜입니다."
    return None


def validate_customer_id(cid):
    """고객사 ID가 C + 3자리 숫자 형식인지 검증한다."""
    if not cid or not isinstance(cid, str) or cid.strip() == '':
        return "[오류] 고객사 ID는 필수 입력값입니다."
    cid = cid.strip()
    pattern = r'^C\d{3}$'
    if not re.match(pattern, cid):
        return "[오류] 고객사 ID 형식이 올바르지 않습니다. (C001 형식으로 입력해주세요)"
    return None


def validate_report_id(rid):
    """영업일지 ID가 R + 3자리 숫자 형식인지 검증한다."""
    if not rid or not isinstance(rid, str) or rid.strip() == '':
        return "[오류] 영업일지 ID는 필수 입력값입니다."
    rid = rid.strip()
    pattern = r'^R\d{3}$'
    if not re.match(pattern, rid):
        return "[오류] 영업일지 ID 형식이 올바르지 않습니다. (R001 형식으로 입력해주세요)"
    return None