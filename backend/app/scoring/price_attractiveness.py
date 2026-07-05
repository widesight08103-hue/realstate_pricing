"""가격 매력도 점수 (0~100).

구성 (DESIGN.md 3장, 초기 휴리스틱 — 실사용 데이터로 가중치 튜닝 필요):
  - discount_score (60%): 전고점(역대 최고 평당가) 대비 현재가 하락폭이 클수록 높은 점수
  - volume_score   (40%): 최근 3개월 거래량이 과거 평균 대비 활발할수록 높은 점수
"""
from dataclasses import dataclass

from app.scoring.series import MonthlyPoint, TransactionLike, build_monthly_series

RECENT_MONTHS = 3
DISCOUNT_WEIGHT = 0.6
VOLUME_WEIGHT = 0.4


def _shift_period(period: str, months_back: int) -> str:
    year, month = map(int, period.split("-"))
    total = year * 12 + (month - 1) - months_back
    y, m = divmod(total, 12)
    return f"{y:04d}-{m + 1:02d}"


def _pct_change(points_by_period: dict[str, MonthlyPoint], latest: MonthlyPoint, months_back: int) -> float | None:
    target_period = _shift_period(latest.period, months_back)
    target = points_by_period.get(target_period)
    if target is None or target.avg_price_per_pyeong == 0:
        return None
    return (latest.avg_price_per_pyeong - target.avg_price_per_pyeong) / target.avg_price_per_pyeong


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


@dataclass
class ScoreDetail:
    discount_pct_from_high: float
    change_1m: float | None
    change_3m: float | None
    change_6m: float | None
    change_1y: float | None
    recent_volume: int
    baseline_volume: float


@dataclass
class ScoreResult:
    score: float
    detail: ScoreDetail


def compute_price_attractiveness(transactions: list[TransactionLike]) -> ScoreResult:
    if not transactions:
        raise ValueError("점수를 계산할 거래 데이터가 없습니다.")

    points = build_monthly_series(transactions)
    points_by_period = {p.period: p for p in points}
    latest = points[-1]

    all_time_high = max(p.avg_price_per_pyeong for p in points)
    discount_pct_from_high = (latest.avg_price_per_pyeong - all_time_high) / all_time_high

    if discount_pct_from_high >= 0:
        # 이번 달이 곧 전고점이거나 이를 경신한 상태 -> 저평가 신호 없음
        discount_score = 0.0
    else:
        discount_score = _clamp(-discount_pct_from_high * 200)

    recent_periods = {p.period for p in points[-RECENT_MONTHS:]}
    recent_volume = sum(p.transaction_count for p in points if p.period in recent_periods)

    baseline_points = [p for p in points if p.period not in recent_periods]
    baseline_volume = (
        sum(p.transaction_count for p in baseline_points) / len(baseline_points)
        if baseline_points
        else float(recent_volume) / RECENT_MONTHS
    )

    volume_ratio = recent_volume / (baseline_volume * RECENT_MONTHS) if baseline_volume > 0 else 1.0
    volume_score = _clamp(volume_ratio * 50)

    score = round(DISCOUNT_WEIGHT * discount_score + VOLUME_WEIGHT * volume_score, 1)

    detail = ScoreDetail(
        discount_pct_from_high=round(discount_pct_from_high * 100, 2),
        change_1m=_pct_change(points_by_period, latest, 1),
        change_3m=_pct_change(points_by_period, latest, 3),
        change_6m=_pct_change(points_by_period, latest, 6),
        change_1y=_pct_change(points_by_period, latest, 12),
        recent_volume=recent_volume,
        baseline_volume=round(baseline_volume, 2),
    )
    return ScoreResult(score=score, detail=detail)
