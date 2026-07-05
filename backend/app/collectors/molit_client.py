"""국토교통부 아파트매매 실거래자료 조회 API(RTMSDataSvcAptTrade) 클라이언트.

공공데이터포털: https://www.data.go.kr/data/15058747/openapi.do
"""
from dataclasses import dataclass
from datetime import date
from xml.etree import ElementTree

import httpx

BASE_URL = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"

# 응답 태그명이 배포 버전에 따라 한글/영문으로 달라질 수 있어 별칭을 둔다.
_FIELD_ALIASES = {
    "apt_name": ["아파트", "aptNm", "aptName"],
    "legal_dong": ["법정동", "umdNm"],
    "jibun": ["지번", "jibun"],
    "area": ["전용면적", "excluUseAr"],
    "floor": ["층", "floor"],
    "build_year": ["건축년도", "buildYear"],
    "deal_amount": ["거래금액", "dealAmount"],
    "deal_year": ["년", "dealYear"],
    "deal_month": ["월", "dealMonth"],
    "deal_day": ["일", "dealDay"],
}


class MolitApiError(Exception):
    pass


@dataclass
class RawTransaction:
    sigungu_code: str
    legal_dong: str
    apt_name: str
    jibun: str | None
    build_year: int | None
    area: float
    floor: int | None
    deal_date: date
    deal_amount: int  # 만원 단위


def _extract(item: ElementTree.Element, field: str) -> str | None:
    for tag in _FIELD_ALIASES[field]:
        el = item.find(tag)
        if el is not None and el.text is not None:
            return el.text.strip()
    return None


def _parse_item(item: ElementTree.Element, sigungu_code: str) -> RawTransaction:
    amount_raw = _extract(item, "deal_amount") or "0"
    amount = int(amount_raw.replace(",", "").strip())

    area_raw = _extract(item, "area")
    floor_raw = _extract(item, "floor")
    build_year_raw = _extract(item, "build_year")

    year = int(_extract(item, "deal_year"))
    month = int(_extract(item, "deal_month"))
    day = int(_extract(item, "deal_day"))

    return RawTransaction(
        sigungu_code=sigungu_code,
        legal_dong=(_extract(item, "legal_dong") or "").strip(),
        apt_name=(_extract(item, "apt_name") or "").strip(),
        jibun=_extract(item, "jibun"),
        build_year=int(build_year_raw) if build_year_raw else None,
        area=float(area_raw),
        floor=int(floor_raw) if floor_raw else None,
        deal_date=date(year, month, day),
        deal_amount=amount,
    )


def parse_response(xml_text: str, sigungu_code: str) -> list[RawTransaction]:
    root = ElementTree.fromstring(xml_text)

    result_code = root.findtext("./header/resultCode")
    if result_code is not None and result_code != "000":
        result_msg = root.findtext("./header/resultMsg")
        raise MolitApiError(f"MOLIT API error {result_code}: {result_msg}")

    items = root.findall("./body/items/item")
    return [_parse_item(item, sigungu_code) for item in items]


def fetch_month(
    service_key: str,
    sigungu_code: str,
    deal_ymd: str,
    *,
    num_of_rows: int = 1000,
    client: httpx.Client | None = None,
) -> list[RawTransaction]:
    """특정 시군구(sigungu_code)·계약월(deal_ymd, 'YYYYMM')의 실거래 내역 전체를 조회한다."""
    owns_client = client is None
    client = client or httpx.Client(timeout=30.0)
    try:
        page_no = 1
        all_transactions: list[RawTransaction] = []
        while True:
            resp = client.get(
                BASE_URL,
                params={
                    "serviceKey": service_key,
                    "LAWD_CD": sigungu_code,
                    "DEAL_YMD": deal_ymd,
                    "pageNo": page_no,
                    "numOfRows": num_of_rows,
                },
            )
            resp.raise_for_status()
            transactions = parse_response(resp.text, sigungu_code)
            all_transactions.extend(transactions)

            root = ElementTree.fromstring(resp.text)
            total_count = int(root.findtext("./body/totalCount") or 0)
            if page_no * num_of_rows >= total_count:
                break
            page_no += 1
        return all_transactions
    finally:
        if owns_client:
            client.close()
