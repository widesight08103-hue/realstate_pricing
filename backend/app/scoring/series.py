from dataclasses import dataclass
from datetime import date
from typing import Protocol

PYEONG_M2 = 3.305785  # 1평 = 3.305785㎡


class TransactionLike(Protocol):
    deal_date: date
    deal_amount: int
    area: float


def price_per_pyeong(deal_amount: int, area_m2: float) -> float:
    """거래금액(만원)을 평당가(만원/평)로 환산."""
    pyeong = area_m2 / PYEONG_M2
    return deal_amount / pyeong


@dataclass
class MonthlyPoint:
    period: str  # "YYYY-MM"
    avg_price_per_pyeong: float
    transaction_count: int


def build_monthly_series(transactions: list[TransactionLike]) -> list[MonthlyPoint]:
    """거래 목록을 계약월별 평균 평당가 시계열로 변환한다. 오름차순 정렬."""
    buckets: dict[str, list[float]] = {}
    for tx in transactions:
        period = f"{tx.deal_date.year:04d}-{tx.deal_date.month:02d}"
        buckets.setdefault(period, []).append(price_per_pyeong(tx.deal_amount, tx.area))

    points = [
        MonthlyPoint(
            period=period,
            avg_price_per_pyeong=sum(prices) / len(prices),
            transaction_count=len(prices),
        )
        for period, prices in buckets.items()
    ]
    points.sort(key=lambda p: p.period)
    return points
