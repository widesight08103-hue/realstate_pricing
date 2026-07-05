from dataclasses import dataclass
from datetime import date

import pytest

from app.scoring.price_attractiveness import compute_price_attractiveness
from app.scoring.series import PYEONG_M2, build_monthly_series

AREA_M2 = 25.0 * PYEONG_M2  # 정확히 25평


@dataclass
class Tx:
    deal_date: date
    deal_amount: int
    area: float


def _month_transactions(period: str, price_per_pyeong: float, count: int) -> list[Tx]:
    year, month = map(int, period.split("-"))
    amount = round(price_per_pyeong * 25.0)
    return [Tx(deal_date=date(year, month, day=d + 1), deal_amount=amount, area=AREA_M2) for d in range(count)]


# (period, 평당가(만원), 거래건수) — 2024-02가 전고점, 2025-02~04가 "최근"(거래량 급증 + 가격 하락)
MONTHLY_SPEC = (
    [("2024-01", 3500, 1)]
    + [("2024-02", 4000, 1)]  # 전고점
    + [(f"2024-{m:02d}", 3500, 1) for m in range(3, 13)]
    + [("2025-01", 3500, 1)]
    + [("2025-02", 3200, 2)]
    + [("2025-03", 3100, 2)]
    + [("2025-04", 3000, 2)]  # 최신월, 전고점 대비 -25%
)


def _build_all_transactions() -> list[Tx]:
    transactions: list[Tx] = []
    for period, price, count in MONTHLY_SPEC:
        transactions.extend(_month_transactions(period, price, count))
    return transactions


def test_build_monthly_series_matches_spec():
    points = build_monthly_series(_build_all_transactions())
    assert len(points) == len(MONTHLY_SPEC)
    assert points[0].period == "2024-01"
    assert points[-1].period == "2025-04"
    assert points[-1].transaction_count == 2
    assert points[-1].avg_price_per_pyeong == pytest.approx(3000, rel=1e-6)


def test_price_attractiveness_score_and_detail():
    result = compute_price_attractiveness(_build_all_transactions())

    # discount_score = 50 (25% 할인), volume_score = 100 (최근 거래량이 기준선의 2배)
    # score = 0.6*50 + 0.4*100 = 70.0
    assert result.score == pytest.approx(70.0)

    detail = result.detail
    assert detail.discount_pct_from_high == pytest.approx(-25.0)
    assert detail.change_1m == pytest.approx((3000 - 3100) / 3100)
    assert detail.change_3m == pytest.approx((3000 - 3500) / 3500)
    assert detail.change_6m == pytest.approx((3000 - 3500) / 3500)
    assert detail.change_1y == pytest.approx((3000 - 3500) / 3500)
    assert detail.recent_volume == 6
    assert detail.baseline_volume == pytest.approx(1.0)


def test_price_attractiveness_at_new_high_has_zero_discount_score():
    transactions = _month_transactions("2024-01", 3000, 1) + _month_transactions("2024-02", 3500, 1)
    result = compute_price_attractiveness(transactions)
    assert result.detail.discount_pct_from_high == pytest.approx(0.0)


def test_compute_price_attractiveness_requires_transactions():
    with pytest.raises(ValueError):
        compute_price_attractiveness([])
