from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from .database import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    merchant_name = Column(String, nullable=True)
    date = Column(String, nullable=True)
    total_amount = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    extracted_json = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )