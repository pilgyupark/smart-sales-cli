import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.validator import validate_required, validate_email


def _generate_customer_id(customers):
    """새 고객사 ID를 자동 생성한다."""
    if not customers:
        return "C001"
    max_num = 0
    for c in customers:
        cid = c.get("customer_id", "")
        if cid.startswith("C") and cid[1:].isdigit():
            num = int(cid[1:])
            if num > max_num:
                max_num = num
    return f"C{max_num + 1:03d}"


def register_customer(customers, name, manager, email):
    """새 고객사를 등록한다.

    Returns:
        (True, 등록된 customer dict) 또는 (False, 오류 메시지)
    """
    # 입력 검증
    err = validate_required(name, "고객사명")
    if err:
        return False, err
    err = validate_required(manager, "담당자명")
    if err:
        return False, err
    err = validate_email(email)
    if err:
        return False, err

    # ID 자동 생성
    customer_id = _generate_customer_id(customers)

    customer = {
        "customer_id": customer_id,
        "customer_name": name.strip(),
        "manager_name": manager.strip(),
        "email": email.strip(),
    }
    customers.append(customer)
    return True, customer


def list_customers(customers):
    """전체 고객사 목록을 반환한다."""
    return list(customers)


def get_customer(customers, customer_id):
    """고객사 ID로 1건을 조회한다."""
    for c in customers:
        if c.get("customer_id") == customer_id:
            return c
    return None


def search_customers(customers, keyword):
    """고객사명, 담당자명, 이메일로 부분 검색한다. (대소문자 구분 없음)"""
    if not keyword or not keyword.strip():
        return list(customers)
    keyword = keyword.strip().lower()
    results = []
    for c in customers:
        if (keyword in c.get("customer_name", "").lower()
                or keyword in c.get("manager_name", "").lower()
                or keyword in c.get("email", "").lower()):
            results.append(c)
    return results


def update_customer(customers, customer_id, name, manager, email):
    """고객사 정보를 수정한다.

    Returns:
        (True, 수정된 customer dict) 또는 (False, 오류 메시지)
    """
    customer = get_customer(customers, customer_id)
    if customer is None:
        return False, "[오류] 존재하지 않는 고객사 ID입니다."

    err = validate_required(name, "고객사명")
    if err:
        return False, err
    err = validate_required(manager, "담당자명")
    if err:
        return False, err
    err = validate_email(email)
    if err:
        return False, err

    customer["customer_name"] = name.strip()
    customer["manager_name"] = manager.strip()
    customer["email"] = email.strip()
    return True, customer


def delete_customer(customers, customer_id):
    """고객사를 삭제한다.

    Returns:
        (True, 성공 메시지) 또는 (False, 오류 메시지)
    """
    for i, c in enumerate(customers):
        if c.get("customer_id") == customer_id:
            customers.pop(i)
            return True, f"[삭제 완료] {customer_id} 고객사가 삭제되었습니다."
    return False, "[오류] 존재하지 않는 고객사 ID입니다."
