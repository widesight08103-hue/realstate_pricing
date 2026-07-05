from datetime import date

import pytest

from app.collectors.molit_client import parse_response, MolitApiError

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <header>
        <resultCode>000</resultCode>
        <resultMsg>OK</resultMsg>
    </header>
    <body>
        <items>
            <item>
                <거래금액>   150,000</거래금액>
                <건축년도>2003</건축년도>
                <년>2025</년>
                <법정동> 개포동</법정동>
                <아파트>개포자이</아파트>
                <월>6</월>
                <일>15</일>
                <전용면적>84.97</전용면적>
                <지번>12</지번>
                <지역코드>11680</지역코드>
                <층>5</층>
            </item>
            <item>
                <거래금액>   82,000</거래금액>
                <건축년도>2003</건축년도>
                <년>2025</년>
                <법정동> 개포동</법정동>
                <아파트>개포자이</아파트>
                <월>6</월>
                <일>20</일>
                <전용면적>59.93</전용면적>
                <지번>12</지번>
                <지역코드>11680</지역코드>
                <층>10</층>
            </item>
        </items>
        <numOfRows>10</numOfRows>
        <pageNo>1</pageNo>
        <totalCount>2</totalCount>
    </body>
</response>
"""

ERROR_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <header>
        <resultCode>30</resultCode>
        <resultMsg>SERVICE KEY IS NOT REGISTERED ERROR</resultMsg>
    </header>
</response>
"""


def test_parse_response_extracts_all_items():
    transactions = parse_response(SAMPLE_XML, sigungu_code="11680")

    assert len(transactions) == 2

    first = transactions[0]
    assert first.apt_name == "개포자이"
    assert first.legal_dong == "개포동"
    assert first.area == 84.97
    assert first.floor == 5
    assert first.deal_amount == 150000
    assert first.deal_date == date(2025, 6, 15)
    assert first.sigungu_code == "11680"
    assert first.build_year == 2003

    second = transactions[1]
    assert second.deal_amount == 82000
    assert second.area == 59.93


def test_parse_response_raises_on_api_error():
    with pytest.raises(MolitApiError):
        parse_response(ERROR_XML, sigungu_code="11680")
