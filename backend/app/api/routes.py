from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Complex, Transaction
from app.schemas import (
    ComplexOut,
    PricePoint,
    PriceSeriesOut,
    ScoreDetail,
    ScoreOut,
)
from app.scoring.price_attractiveness import compute_price_attractiveness
from app.scoring.series import build_monthly_series

router = APIRouter(prefix="/api")


@router.get("/complexes", response_model=list[ComplexOut])
def search_complexes(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return (
        db.query(Complex)
        .filter(Complex.name.ilike(f"%{query}%"))
        .order_by(Complex.name)
        .limit(50)
        .all()
    )


@router.get("/complexes/{complex_id}", response_model=ComplexOut)
def get_complex(complex_id: int, db: Session = Depends(get_db)):
    complex_ = db.get(Complex, complex_id)
    if complex_ is None:
        raise HTTPException(status_code=404, detail="단지를 찾을 수 없습니다.")
    return complex_


@router.get("/complexes/{complex_id}/areas")
def list_areas(complex_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(Transaction.area, func.count(Transaction.id))
        .filter(Transaction.complex_id == complex_id)
        .group_by(Transaction.area)
        .order_by(Transaction.area)
        .all()
    )
    if not rows:
        raise HTTPException(status_code=404, detail="해당 단지의 거래 데이터가 없습니다.")
    return [{"area": area, "transaction_count": count} for area, count in rows]


def _get_transactions_for_area(db: Session, complex_id: int, area: float) -> list[Transaction]:
    transactions = (
        db.query(Transaction)
        .filter(Transaction.complex_id == complex_id, Transaction.area == area)
        .order_by(Transaction.deal_date)
        .all()
    )
    if not transactions:
        raise HTTPException(status_code=404, detail="해당 조건의 거래 데이터가 없습니다.")
    return transactions


@router.get("/complexes/{complex_id}/price-series", response_model=PriceSeriesOut)
def get_price_series(complex_id: int, area: float, db: Session = Depends(get_db)):
    transactions = _get_transactions_for_area(db, complex_id, area)
    points = build_monthly_series(transactions)
    return PriceSeriesOut(
        complex_id=complex_id,
        area=area,
        points=[
            PricePoint(
                period=p.period,
                avg_price_per_pyeong=round(p.avg_price_per_pyeong, 1),
                transaction_count=p.transaction_count,
            )
            for p in points
        ],
    )


@router.get("/complexes/{complex_id}/score", response_model=ScoreOut)
def get_score(complex_id: int, area: float, db: Session = Depends(get_db)):
    transactions = _get_transactions_for_area(db, complex_id, area)
    result = compute_price_attractiveness(transactions)
    return ScoreOut(
        complex_id=complex_id,
        area=area,
        score=result.score,
        detail=ScoreDetail(**result.detail.__dict__),
    )
