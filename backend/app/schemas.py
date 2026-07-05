from datetime import date
from pydantic import BaseModel


class ComplexOut(BaseModel):
    id: int
    name: str
    legal_dong: str
    sigungu_code: str
    jibun: str | None
    build_year: int | None

    model_config = {"from_attributes": True}


class TransactionOut(BaseModel):
    deal_date: date
    area: float
    floor: int | None
    deal_amount: int

    model_config = {"from_attributes": True}


class PricePoint(BaseModel):
    period: str  # "YYYY-MM"
    avg_price_per_pyeong: float  # 평당가(만원/평)
    transaction_count: int


class PriceSeriesOut(BaseModel):
    complex_id: int
    area: float
    points: list[PricePoint]


class ScoreDetail(BaseModel):
    discount_pct_from_high: float  # 전고점 대비 현재 %(음수=하락)
    change_1m: float | None
    change_3m: float | None
    change_6m: float | None
    change_1y: float | None
    recent_volume: int
    baseline_volume: float


class ScoreOut(BaseModel):
    complex_id: int
    area: float
    score: float
    detail: ScoreDetail
