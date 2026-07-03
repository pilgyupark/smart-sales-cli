import re


def validate_required(value, field_name):
    """필수 입력값이 비어있지 않은지 검증한다."""
    if value is None or (isinstance(value, str) and value.strip() == ''):
        return f"[오류] {field_name}은(는) 필수 입력값입니다."
    return None


def validate_email(email):
    """이메일 형식을 검증한다. (공개 함수)

    Returns:
        오류 메시지 또는 None (정상)
    """
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