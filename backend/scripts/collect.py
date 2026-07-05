"""수동/배치 실행용 수집 스크립트.

사용 예:
    python -m scripts.collect --ymd 202506
    python -m scripts.collect --ymd 202506 --lawd 11680
"""
import argparse
import sys

from app.collectors.law_codes import get_region_codes
from app.collectors.molit_client import fetch_month, MolitApiError
from app.collectors.ingest import ingest_transactions
from app.config import settings
from app.db import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ymd", required=True, help="계약년월 YYYYMM")
    parser.add_argument("--lawd", help="법정동코드(5자리). 생략 시 등록된 전체 지역 수집")
    args = parser.parse_args()

    if not settings.molit_service_key:
        print("MOLIT_SERVICE_KEY가 설정되지 않았습니다. .env를 확인하세요.", file=sys.stderr)
        raise SystemExit(1)

    region_codes = get_region_codes()
    targets = {args.lawd: region_codes.get(args.lawd, "")} if args.lawd else region_codes

    db = SessionLocal()
    try:
        for code, name in targets.items():
            try:
                transactions = fetch_month(settings.molit_service_key, code, args.ymd)
            except MolitApiError as e:
                print(f"[{code} {name}] 수집 실패: {e}", file=sys.stderr)
                continue
            inserted = ingest_transactions(db, transactions)
            print(f"[{code} {name}] {len(transactions)}건 조회, {inserted}건 신규 저장")
    finally:
        db.close()


if __name__ == "__main__":
    main()
