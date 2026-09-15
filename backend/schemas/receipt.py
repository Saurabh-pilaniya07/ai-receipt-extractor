from pydantic import BaseModel, Field


class LineItem(BaseModel):
    item_name: str
    price: float


class ReceiptExtraction(BaseModel):
    merchant_name: str | None = None
    date: str | None = None
    line_items: list[LineItem] = Field(default_factory=list)
    total_amount: float | None = None
    tax: float | None = None
    tip: float | None = None