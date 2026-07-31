from datetime import datetime
from typing import Any, Optional
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel
from database.postgres import engine


class SalesTransaction(SQLModel, table=True):
    """SQLModel ORM model representing explicit 16-column sales transaction records."""

    __tablename__ = "sales_transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: str = Field(index=True)
    order_id: str = Field(index=True)
    customer_id: str = Field(index=True)
    product_name: str
    category: str
    price: float
    quantity_sold: int
    total_sales: float
    order_date: datetime
    payment_method: str
    customer_rating: float
    month: str
    year: int
    profit: float
    discount: float
    customer_segment: str
    region: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SalesAnalyticsSummary(SQLModel, table=True):
    """SQLModel ORM model representing pre-computed quantitative sales summary metrics."""

    __tablename__ = "sales_analytics_summary"

    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: str = Field(index=True)
    metrics: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


def init_db() -> None:
    """Initializes database tables using SQLModel metadata."""
    SQLModel.metadata.create_all(engine)
