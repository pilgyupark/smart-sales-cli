import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils.file_handler import load_data, save_data
import customer_service
import sales_report_service
from models.customer import (
    search_customers,
)
from models.report import (
    submit_report,
    approve_report,
    reject_report,
    withdraw_report,
)

CUSTOMER_FILE = "data/customers.json"
REPORT_FILE = "data/sales_reports.json"


def print_menu():
    print("\n=== Smart Sales CLI ===")
    print("1. 고객사 등록")
    print("2. 고객사 목록")
    print("3. 고객사 검색")
    print("4. 고객사 상세 조회")
    print("5. 고객사 수정")
    print("6. 고객사 삭제")
    print("7. 영업일지 등록")
    print("8. 영업일지 목록")
    print("9. 영업일지 수정")
    print("10. 영업일지 상신")
    print("11. 영업일지 승인")
    print("12. 영업일지 반려")
    print("13. 영업일지 회수")
    print("14. 고객사별 활동 요약")
    print("15. CSV 내보내기")
    print("0. 종료")
    print("=" * 27)


def print_customer_header():
    print(f"{'ID':<8} {'고객사명':<16} {'담당자':<12} {'이메일':<24}")
    print("-" * 60)


def print_customer_row(c):
    print(f"{c['customer_id']:<8} {c['customer_name']:<16} "
          f"{c['manager_name']:<12} {c['email']:<24}")


def print_report_header():
    print(f"{'ID':<8} {'고객사ID':<10} {'날짜':<12} {'내용':<20} {'상태':<12}")
    print("-" * 62)


def print_report_row(r):
    print(f"{r['report_id']:<8} {r['customer_id']:<10} "
          f"{r['activity_date']:<12} {r['content']:<20} {r['status']:<12}")


def handle_register_customer():
    name = input("고객사명: ").strip()
    manager = input("담당자명: ").strip()
    email = input("이메일: ").strip()
    success, result = customer_service.register_customer(name, manager, email)
    if success:
        print(f"[등록 완료] {result['customer_id']} - {result['customer_name']}")
    else:
        print(result)


def handle_list_customers():
    customers = customer_service.list_customers()
    if not customers:
        print("[안내] 등록된 고객사가 없습니다.")
        return
    print_customer_header()
    for c in customers:
        print_customer_row(c)


def handle_search_customer():
    customers = customer_service.list_customers()
    keyword = input("검색어 (고객사명/담당자명/이메일): ").strip()
    results = search_customers(customers, keyword)
    if not results:
        print("[안내] 검색 결과가 없습니다.")
        return
    print_customer_header()
    for c in results:
        print_customer_row(c)


def handle_get_customer():
    cid = input("고객사 ID: ").strip()
    customer = customer_service.get_customer(cid)
    if customer is None:
        print("[오류] 존재하지 않는 고객사 ID입니다.")
        return
    print_customer_header()
    print_customer_row(customer)


def handle_update_customer():
    cid = input("고객사 ID: ").strip()
    name = input("새 고객사명: ").strip()
    manager = input("새 담당자명: ").strip()
    email = input("새 이메일: ").strip()
    success, result = customer_service.update_customer(cid, name, manager, email)
    if success:
        print(f"[수정 완료] {result['customer_id']} - {result['customer_name']}")
    else:
        print(result)


def handle_delete_customer():
    cid = input("고객사 ID: ").strip()
    success, message = customer_service.delete_customer(cid)
    print(message)


def handle_register_report():
    cid = input("고객사 ID: ").strip()
    date = input("활동 날짜 (YYYY-MM-DD): ").strip()
    content = input("영업 내용: ").strip()
    success, result = sales_report_service.register_report(cid, date, content)
    if success:
        print(f"[등록 완료] {result['report_id']} - {result['content']}")
    else:
        print(result)


def handle_list_reports():
    reports = sales_report_service.list_reports()
    if not reports:
        print("[안내] 등록된 영업일지가 없습니다.")
        return
    print_report_header()
    for r in reports:
        print_report_row(r)


def handle_update_report():
    rid = input("영업일지 ID: ").strip()
    date = input("새 활동 날짜 (YYYY-MM-DD): ").strip()
    content = input("새 영업 내용: ").strip()
    success, result = sales_report_service.update_report(rid, date, content)
    if success:
        print(f"[수정 완료] {result['report_id']}")
    else:
        print(result)


def handle_submit_report(reports):
    rid = input("영업일지 ID: ").strip()
    success, message = submit_report(reports, rid)
    print(message)


def handle_approve_report(reports):
    rid = input("영업일지 ID: ").strip()
    success, message = approve_report(reports, rid)
    print(message)


def handle_reject_report(reports):
    rid = input("영업일지 ID: ").strip()
    success, message = reject_report(reports, rid)
    print(message)


def handle_withdraw_report(reports):
    rid = input("영업일지 ID: ").strip()
    success, message = withdraw_report(reports, rid)
    print(message)


def handle_customer_summary():
    """고객사별 활동 요약을 출력한다."""
    reports = sales_report_service.list_reports()
    if not reports:
        print("[안내] 등록된 영업일지가 없습니다.")
        return
    summary = {}
    for r in reports:
        cid = r["customer_id"]
        if cid not in summary:
            customer = customer_service.get_customer(cid)
            name = customer["customer_name"] if customer else cid
            summary[cid] = {"name": name, "total": 0, "draft": 0,
                            "submitted": 0, "approved": 0, "rejected": 0}
        summary[cid]["total"] += 1
        status_key = r["status"].lower()
        if status_key in summary[cid]:
            summary[cid][status_key] += 1

    print(f"\n{'고객사ID':<10} {'고객사명':<16} {'전체':<6} {'DRAFT':<8} "
          f"{'SUBMITTED':<12} {'APPROVED':<10} {'REJECTED':<10}")
    print("-" * 72)
    for cid, data in summary.items():
        print(f"{cid:<10} {data['name']:<16} {data['total']:<6} "
              f"{data['draft']:<8} {data['submitted']:<12} "
              f"{data['approved']:<10} {data['rejected']:<10}")


def handle_export_csv():
    """고객사 목록을 CSV로 내보낸다."""
    import csv
    customers = customer_service.list_customers()
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    path = os.path.join(export_dir, "customers.csv")
    try:
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["customer_id", "customer_name", "manager_name", "email"])
            for c in customers:
                writer.writerow([c["customer_id"], c["customer_name"],
                                 c["manager_name"], c["email"]])
        print(f"[내보내기 완료] {path}")
    except IOError as e:
        print(f"[오류] CSV 파일 저장 실패: {e}")


def main():
    while True:
        print_menu()
        choice = input("메뉴 선택: ").strip()

        if choice == "0":
            print("[종료] 프로그램을 종료합니다.")
            break
        elif choice == "1":
            handle_register_customer()
        elif choice == "2":
            handle_list_customers()
        elif choice == "3":
            handle_search_customer()
        elif choice == "4":
            handle_get_customer()
        elif choice == "5":
            handle_update_customer()
        elif choice == "6":
            handle_delete_customer()
        elif choice == "7":
            handle_register_report()
        elif choice == "8":
            handle_list_reports()
        elif choice == "9":
            handle_update_report()
        elif choice == "10":
            handle_submit_report(sales_report_service.list_reports())
        elif choice == "11":
            handle_approve_report(sales_report_service.list_reports())
        elif choice == "12":
            handle_reject_report(sales_report_service.list_reports())
        elif choice == "13":
            handle_withdraw_report(sales_report_service.list_reports())
        elif choice == "14":
            handle_customer_summary()
        elif choice == "15":
            handle_export_csv()
        else:
            print("[오류] 올바른 메뉴 번호를 입력해주세요.")


if __name__ == "__main__":
    main()