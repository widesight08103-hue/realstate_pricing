"""법정동코드(시군구, 5자리) 매핑.

MOLIT 실거래가 API는 LAWD_CD(법정동코드 앞 5자리)로 지역을 지정한다.
서울 25개 자치구는 안정적으로 알려진 코드라 하드코딩했고, 경기/인천 등
나머지 수도권 시군구는 공공데이터포털이 배포하는 법정동코드 전체 목록
(https://www.code.go.kr) CSV를 backend/app/collectors/law_codes_extra.csv
로 받아 추가할 수 있도록 로더를 제공한다. 잘못된 코드로 조용히 수집되는
것을 막기 위해 검증되지 않은 경기/인천 코드는 여기에 직접 넣지 않았다.
"""
import csv
from pathlib import Path

SEOUL_GU_CODES: dict[str, str] = {
    "11110": "종로구",
    "11140": "중구",
    "11170": "용산구",
    "11200": "성동구",
    "11215": "광진구",
    "11230": "동대문구",
    "11260": "중랑구",
    "11290": "성북구",
    "11305": "강북구",
    "11320": "도봉구",
    "11350": "노원구",
    "11380": "은평구",
    "11410": "서대문구",
    "11440": "마포구",
    "11470": "양천구",
    "11500": "강서구",
    "11530": "구로구",
    "11545": "금천구",
    "11560": "영등포구",
    "11590": "동작구",
    "11620": "관악구",
    "11650": "서초구",
    "11680": "강남구",
    "11710": "송파구",
    "11740": "강동구",
}

_EXTRA_CSV_PATH = Path(__file__).with_name("law_codes_extra.csv")


def load_extra_codes(path: Path = _EXTRA_CSV_PATH) -> dict[str, str]:
    """path의 CSV(code,name 헤더)에서 추가 법정동코드를 읽는다. 파일이 없으면 빈 dict."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["code"]: row["name"] for row in reader}


def get_region_codes() -> dict[str, str]:
    codes = dict(SEOUL_GU_CODES)
    codes.update(load_extra_codes())
    return codes
