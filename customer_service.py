import json
import os

from validators import validate_required, validate_email

CUSTOMER_FILE = "data/customers.json"


def _load_customers():
    """고객사 데이터를 JSON 파일에서 로드한다."""
    if not os.path.exists(CUSTOMER_FILE):
        return []
    try:
        with open(CUSTOMER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_customers(customers):
    """고객사 데이터를 JSON 파일에 저장한다."""
    os.makedirs(os.path.dirname(CUSTOMER_FILE), exist_ok=True)
    with open(CUSTOMER_FILE, 'w', encoding='utf-8') as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)


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


def register_customer(name, manager, email):
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

    customers = _load_customers()

    # ID 자동 생성
    customer_id = _generate_customer_id(customers)

    # 중복 ID 차단 (자동 생성이므로 거의 발생하지 않지만 안전장치)
    for c in customers:
        if c.get("customer_id") == customer_id:
            return False, f"[오류] {customer_id}는 이미 존재하는 고객사 ID입니다."

    customer = {
        "customer_id": customer_id,
        "customer_name": name.strip(),
        "manager_name": manager.strip(),
        "email": email.strip(),
    }
    customers.append(customer)
    _save_customers(customers)
    return True, customer


def list_customers():
    """전체 고객사 목록을 반환한다."""
    return _load_customers()


def get_customer(customer_id):
    """고객사 ID로 1건을 조회한다."""
    customers = _load_customers()
    for c in customers:
        if c.get("customer_id") == customer_id:
            return c
    return None


def update_customer(customer_id, name, manager, email):
    """고객사 정보를 수정한다.

    Returns:
        (True, 수정된 customer dict) 또는 (False, 오류 메시지)
    """
    customers = _load_customers()

    target = None
    for c in customers:
        if c.get("customer_id") == customer_id:
            target = c
            break

    if target is None:
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

    target["customer_name"] = name.strip()
    target["manager_name"] = manager.strip()
    target["email"] = email.strip()
    _save_customers(customers)
    return True, target


def delete_customer(customer_id):
    """고객사를 삭제한다.

    Returns:
        (True, 성공 메시지) 또는 (False, 오류 메시지)
    """
    customers = _load_customers()
    for i, c in enumerate(customers):
        if c.get("customer_id") == customer_id:
            customers.pop(i)
            _save_customers(customers)
            return True, f"[삭제 완료] {customer_id} 고객사가 삭제되었습니다."
    return False, "[오류] 존재하지 않는 고객사 ID입니다."