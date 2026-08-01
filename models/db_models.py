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


class CustomerRecord(SQLModel, table=True):
    """SQLModel ORM model representing customer dataset records."""

    __tablename__ = "customer_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: str = Field(index=True)
    customer_id: str = Field(index=True)
    customer_name: str
    customer_segment: str
    region: str
    city: str
    join_date: Optional[datetime] = None
    customer_status: str
    loyalty_tier: str
    customer_rating: float
    churn_risk: str
    preferred_payment_method: str
    total_orders: float
    total_spend: float
    average_order_value: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CustomerAnalyticsSummary(SQLModel, table=True):
    """SQLModel ORM model representing pre-computed quantitative customer summary metrics."""

    __tablename__ = "customer_analytics_summary"

    id: Optional[int] = Field(default=None, primary_key=True)
    batch_id: str = Field(index=True)
    metrics: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


def init_db() -> None:
    """Initializes database tables using SQLModel metadata."""
    SQLModel.metadata.create_all(engine)
