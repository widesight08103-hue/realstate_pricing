from datetime import date, datetime

from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Float,
    String,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db import Base


class Complex(Base):
    """아파트 단지. MOLIT 데이터에는 안정적인 단지ID가 없으므로
    (법정동코드, 법정동, 단지명, 지번)으로 식별한다."""

    __tablename__ = "complexes"
    __table_args__ = (
        UniqueConstraint("sigungu_code", "legal_dong", "name", "jibun", name="uq_complex_identity"),
    )

    id = Column(Integer, primary_key=True)
    sigungu_code = Column(String(5), nullable=False, index=True)  # 법정동코드(시군구, 5자리)
    legal_dong = Column(String(50), nullable=False)  # 법정동명
    name = Column(String(200), nullable=False, index=True)  # 아파트명
    jibun = Column(String(50), nullable=True)  # 지번
    build_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="complex")
    scores = relationship("Score", back_populates="complex")


class Transaction(Base):
    """국토부 실거래가 원자료 한 건."""

    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint(
            "complex_id", "area", "floor", "deal_date", "deal_amount",
            name="uq_transaction_identity",
        ),
    )

    id = Column(BigInteger, primary_key=True)
    complex_id = Column(Integer, ForeignKey("complexes.id"), nullable=False, index=True)
    area = Column(Float, nullable=False)  # 전용면적(㎡)
    floor = Column(Integer, nullable=True)
    deal_date = Column(Date, nullable=False, index=True)
    deal_amount = Column(BigInteger, nullable=False)  # 거래금액(만원)
    created_at = Column(DateTime, default=datetime.utcnow)

    complex = relationship("Complex", back_populates="transactions")


class Score(Base):
    """단지별 산출 점수 스냅샷."""

    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("complex_id", "score_type", "computed_at", name="uq_score_snapshot"),
    )

    id = Column(Integer, primary_key=True)
    complex_id = Column(Integer, ForeignKey("complexes.id"), nullable=False, index=True)
    score_type = Column(String(50), nullable=False)  # 예: 'price_attractiveness'
    value = Column(Float, nullable=False)
    detail = Column(String, nullable=True)  # 계산 근거 요약(JSON 문자열)
    computed_at = Column(DateTime, default=datetime.utcnow, index=True)

    complex = relationship("Complex", back_populates="scores")
