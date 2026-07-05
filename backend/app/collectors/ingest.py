from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.collectors.molit_client import RawTransaction
from app.models import Complex, Transaction


def _get_or_create_complex(db: Session, tx: RawTransaction) -> Complex:
    complex_ = (
        db.query(Complex)
        .filter_by(
            sigungu_code=tx.sigungu_code,
            legal_dong=tx.legal_dong,
            name=tx.apt_name,
            jibun=tx.jibun,
        )
        .first()
    )
    if complex_ is None:
        complex_ = Complex(
            sigungu_code=tx.sigungu_code,
            legal_dong=tx.legal_dong,
            name=tx.apt_name,
            jibun=tx.jibun,
            build_year=tx.build_year,
        )
        db.add(complex_)
        db.flush()  # id 확보
    return complex_


def ingest_transactions(db: Session, transactions: list[RawTransaction]) -> int:
    """RawTransaction 목록을 DB에 적재한다. 이미 존재하는 거래는 건너뛴다.
    반환값: 새로 삽입된 거래 건수."""
    inserted = 0
    for tx in transactions:
        complex_ = _get_or_create_complex(db, tx)

        exists = (
            db.query(Transaction)
            .filter_by(
                complex_id=complex_.id,
                area=tx.area,
                floor=tx.floor,
                deal_date=tx.deal_date,
                deal_amount=tx.deal_amount,
            )
            .first()
        )
        if exists is not None:
            continue

        db.add(
            Transaction(
                complex_id=complex_.id,
                area=tx.area,
                floor=tx.floor,
                deal_date=tx.deal_date,
                deal_amount=tx.deal_amount,
            )
        )
        try:
            db.flush()
            inserted += 1
        except IntegrityError:
            db.rollback()

    db.commit()
    return inserted
