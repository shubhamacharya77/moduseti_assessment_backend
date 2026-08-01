from datetime import datetime
from typing import Any
import pandas as pd
from sqlmodel import Session, select
from database.postgres import engine
from models.db_models import (
    CustomerAnalyticsSummary,
    CustomerRecord,
    SalesAnalyticsSummary,
    SalesTransaction,
    init_db,
)

# ---------------------------------------------------------------------------
# Column Alias Mapping for Enterprise Sales Datasets (e.g. sales_transactions.csv)
# ---------------------------------------------------------------------------
COLUMN_ALIAS_MAP: dict[str, str] = {
    "order id": "OrderID",
    "order_id": "OrderID",
    "customer_id": "CustomerID",
    "customer id": "CustomerID",
    "product name": "Product",
    "product_name": "Product",
    "product": "Product",
    "category": "Category",
    "price (inr)": "UnitPrice",
    "price": "UnitPrice",
    "quantity sold": "Units",
    "quantity_sold": "Units",
    "units": "Units",
    "total sales (inr)": "Revenue",
    "total_sales": "Revenue",
    "revenue": "Revenue",
    "order date": "Date",
    "order_date": "Date",
    "date": "Date",
    "payment method": "PaymentMethod",
    "payment_method": "PaymentMethod",
    "customer rating": "CustomerRating",
    "customer_rating": "CustomerRating",
    "month": "Month",
    "year": "Year",
    "profit (inr)": "Profit",
    "profit": "Profit",
    "discount %": "Discount",
    "discount": "Discount",
    "customer segment": "CustomerSegment",
    "customer_segment": "CustomerSegment",
    "region": "Region",
    "salesrep": "SalesRep",
    "sales_rep": "SalesRep",
}

DEFAULT_REQUIRED_COLUMNS: list[str] = [
    "Date",
    "Product",
    "Category",
    "Revenue",
    "Units",
    "Profit",
    "Region",
    "CustomerSegment",
]

# ---------------------------------------------------------------------------
# Column Alias Mapping for Enterprise Customer Datasets (e.g. customers.csv)
# ---------------------------------------------------------------------------
CUSTOMER_COLUMN_ALIAS_MAP: dict[str, str] = {
    "customer_id": "CustomerID",
    "customer id": "CustomerID",
    "customer_name": "CustomerName",
    "customer name": "CustomerName",
    "customer_segment": "CustomerSegment",
    "customer segment": "CustomerSegment",
    "region": "Region",
    "city": "City",
    "join_date": "JoinDate",
    "join date": "JoinDate",
    "customer_status": "CustomerStatus",
    "customer status": "CustomerStatus",
    "loyalty_tier": "LoyaltyTier",
    "loyalty tier": "LoyaltyTier",
    "customer_rating": "CustomerRating",
    "customer rating": "CustomerRating",
    "churn_risk": "ChurnRisk",
    "churn risk": "ChurnRisk",
    "churn_status": "ChurnRisk",
    "preferred_payment_method": "PreferredPaymentMethod",
    "preferred payment method": "PreferredPaymentMethod",
    "total_orders": "TotalOrders",
    "total orders": "TotalOrders",
    "total_spend": "TotalSpend",
    "total spend": "TotalSpend",
    "monthly_spend": "TotalSpend",
    "average_order_value": "AverageOrderValue",
    "average order value": "AverageOrderValue",
}


def clean_and_process_sales_csv(
    df: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Cleans and normalizes a raw Sales DataFrame in a fault-tolerant manner."""
    total_raw_rows = len(df)
    if total_raw_rows == 0:
        empty_report = {
            "total_rows_received": 0,
            "processed_rows": 0,
            "skipped_rows": 0,
            "message": "Uploaded CSV contains no rows.",
        }
        return pd.DataFrame(), empty_report

    df = df.copy()

    # Clean raw column names
    raw_columns = [str(col).strip().replace('"', '').replace("'", '') for col in df.columns]
    df.columns = raw_columns

    cleaned_df = pd.DataFrame()

    for original_col in df.columns:
        norm_key = original_col.lower().strip()
        standard_name = COLUMN_ALIAS_MAP.get(norm_key, original_col)
        cleaned_df[standard_name] = df[original_col].copy()

    if "Date" not in cleaned_df.columns:
        cleaned_df["Date"] = pd.Timestamp.now()
    if "Product" not in cleaned_df.columns:
        cleaned_df["Product"] = "Unassigned"
    if "Category" not in cleaned_df.columns:
        cleaned_df["Category"] = "General"
    if "Revenue" not in cleaned_df.columns:
        cleaned_df["Revenue"] = 0.0
    if "Units" not in cleaned_df.columns:
        cleaned_df["Units"] = 1
    if "Profit" not in cleaned_df.columns:
        cleaned_df["Profit"] = 0.0
    if "Region" not in cleaned_df.columns:
        cleaned_df["Region"] = "Unassigned"
    if "CustomerSegment" not in cleaned_df.columns:
        cleaned_df["CustomerSegment"] = "Unassigned"

    for num_col in ["Revenue", "Profit", "UnitPrice", "Discount", "CustomerRating"]:
        if num_col in cleaned_df.columns:
            num_str = (
                cleaned_df[num_col]
                .astype(str)
                .str.replace('"', "", regex=False)
                .str.replace("'", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            cleaned_df[num_col] = pd.to_numeric(num_str, errors="coerce")

    if "Units" in cleaned_df.columns:
        units_str = (
            cleaned_df["Units"]
            .astype(str)
            .str.replace('"', "", regex=False)
            .str.replace("'", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        cleaned_df["Units"] = pd.to_numeric(units_str, errors="coerce")

    cleaned_df["Date"] = pd.to_datetime(cleaned_df["Date"], format="mixed", errors="coerce")

    for text_col in ["Product", "Category", "Region", "CustomerSegment", "PaymentMethod", "CustomerID", "OrderID"]:
        if text_col in cleaned_df.columns:
            cleaned_df[text_col] = (
                cleaned_df[text_col]
                .fillna("Unassigned")
                .astype(str)
                .str.replace('"', "", regex=False)
                .str.replace("'", "", regex=False)
                .str.strip()
            )

    valid_mask = (
        cleaned_df["Revenue"].notna()
        & cleaned_df["Units"].notna()
        & cleaned_df["Date"].notna()
    )
    final_df = cleaned_df[valid_mask].copy()

    processed_rows = len(final_df)
    skipped_rows = total_raw_rows - processed_rows

    report = {
        "total_rows_received": total_raw_rows,
        "processed_rows": processed_rows,
        "skipped_rows": skipped_rows,
        "message": f"CSV processed successfully. {processed_rows} valid rows ingested, {skipped_rows} incomplete rows skipped."
    }

    return final_df, report


def calculate_sales_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """Calculates comprehensive quantitative sales KPIs over cleaned sales transactions."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "profit_margin_pct": 0.0,
            "total_units": 0,
            "total_transactions": 0,
            "average_deal_size": 0.0,
            "average_customer_rating": 0.0,
            "product_breakdown": {},
            "category_breakdown": {},
            "regional_breakdown": {},
            "segment_breakdown": {},
            "top_product": "None",
            "top_category": "None",
            "top_region": "None",
            "monthly_revenue_trends": {},
        }

    total_revenue = float(df["Revenue"].sum())
    total_profit = float(df["Profit"].sum()) if "Profit" in df.columns else 0.0
    profit_margin_pct = round((total_profit / total_revenue) * 100, 2) if total_revenue > 0 else 0.0
    total_units = int(df["Units"].sum())
    total_transactions = int(len(df))
    average_deal_size = round(total_revenue / total_transactions, 2) if total_transactions > 0 else 0.0
    avg_rating = round(float(df["CustomerRating"].mean()), 2) if "CustomerRating" in df.columns and not df["CustomerRating"].isna().all() else 0.0

    product_series = df.groupby("Product")["Revenue"].sum().round(2)
    product_breakdown = product_series.to_dict()
    top_product = str(product_series.idxmax()) if not product_series.empty else "None"

    category_series = df.groupby("Category")["Revenue"].sum().round(2) if "Category" in df.columns else pd.Series()
    category_breakdown = category_series.to_dict() if not category_series.empty else {}
    top_category = str(category_series.idxmax()) if not category_series.empty else "None"

    regional_series = df.groupby("Region")["Revenue"].sum().round(2)
    regional_breakdown = regional_series.to_dict()
    top_region = str(regional_series.idxmax()) if not regional_series.empty else "None"

    segment_series = df.groupby("CustomerSegment")["Revenue"].sum().round(2) if "CustomerSegment" in df.columns else pd.Series()
    segment_breakdown = segment_series.to_dict() if not segment_series.empty else {}

    temp_df = df.copy()
    temp_df["YearMonth"] = temp_df["Date"].dt.strftime("%Y-%m")
    monthly_series = temp_df.groupby("YearMonth")["Revenue"].sum().round(2)
    monthly_revenue_trends = monthly_series.to_dict()

    return {
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "profit_margin_pct": profit_margin_pct,
        "total_units": total_units,
        "total_transactions": total_transactions,
        "average_deal_size": average_deal_size,
        "average_customer_rating": avg_rating,
        "product_breakdown": product_breakdown,
        "category_breakdown": category_breakdown,
        "regional_breakdown": regional_breakdown,
        "segment_breakdown": segment_breakdown,
        "top_product": top_product,
        "top_category": top_category,
        "top_region": top_region,
        "monthly_revenue_trends": monthly_revenue_trends,
    }


def query_sales_analytics(
    df: pd.DataFrame,
    product: str | None = None,
    category: str | None = None,
    region: str | None = None,
    segment: str | None = None
) -> dict[str, Any]:
    """Runs on-the-fly dynamic slice aggregation over sales records."""
    if df.empty:
        return {"total_revenue": 0.0, "total_units": 0, "matching_transactions": 0}

    filtered_df = df.copy()

    if product and "Product" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Product"].str.lower() == product.strip().lower()]
    if category and "Category" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Category"].str.lower() == category.strip().lower()]
    if region and "Region" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Region"].str.lower() == region.strip().lower()]
    if segment and "CustomerSegment" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["CustomerSegment"].str.lower() == segment.strip().lower()]

    if filtered_df.empty:
        return {
            "filters_applied": {"product": product, "category": category, "region": region, "segment": segment},
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "total_units": 0,
            "matching_transactions": 0,
            "monthly_trends": {},
        }

    total_rev = float(filtered_df["Revenue"].sum())
    total_prof = float(filtered_df["Profit"].sum()) if "Profit" in filtered_df.columns else 0.0
    total_u = int(filtered_df["Units"].sum())
    count = int(len(filtered_df))

    temp_df = filtered_df.copy()
    temp_df["YearMonth"] = temp_df["Date"].dt.strftime("%Y-%m")
    monthly_trends = temp_df.groupby("YearMonth")["Revenue"].sum().round(2).to_dict()

    return {
        "filters_applied": {"product": product, "category": category, "region": region, "segment": segment},
        "total_revenue": round(total_rev, 2),
        "total_profit": round(total_prof, 2),
        "profit_margin_pct": round((total_prof / total_rev) * 100, 2) if total_rev > 0 else 0.0,
        "total_units": total_u,
        "matching_transactions": count,
        "average_deal_size": round(total_rev / count, 2) if count > 0 else 0.0,
        "monthly_trends": monthly_trends,
    }


def persist_sales_data_to_db(
    clean_df: pd.DataFrame,
    metrics: dict[str, Any]
) -> str:
    """Persists cleaned sales transactions and pre-computed metrics into DB using SQLModel."""
    init_db()

    batch_id = f"sales_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    with Session(engine) as session:
        transactions = []
        for _, row in clean_df.iterrows():
            tx = SalesTransaction(
                batch_id=batch_id,
                order_id=str(row.get("OrderID", "ORD00000")),
                customer_id=str(row.get("CustomerID", "C0000")),
                product_name=str(row.get("Product", "Unassigned")),
                category=str(row.get("Category", "General")),
                price=float(row.get("UnitPrice", 0.0)),
                quantity_sold=int(row.get("Units", 1)),
                total_sales=float(row.get("Revenue", 0.0)),
                order_date=pd.to_datetime(row.get("Date", pd.Timestamp.now())).to_pydatetime(),
                payment_method=str(row.get("PaymentMethod", "Unknown")),
                customer_rating=float(row.get("CustomerRating", 0.0)),
                month=str(row.get("Month", "Unknown")),
                year=int(row.get("Year", datetime.utcnow().year)),
                profit=float(row.get("Profit", 0.0)),
                discount=float(row.get("Discount", 0.0)),
                customer_segment=str(row.get("CustomerSegment", "Unassigned")),
                region=str(row.get("Region", "Unassigned")),
            )
            transactions.append(tx)

        session.add_all(transactions)

        summary = SalesAnalyticsSummary(
            batch_id=batch_id,
            metrics=metrics
        )
        session.add(summary)

        session.commit()

    return batch_id


def get_latest_sales_transactions_df() -> pd.DataFrame:
    """Queries stored transaction SQLModel records from DB and loads into a clean Pandas DataFrame."""
    init_db()

    with Session(engine) as session:
        statement = select(SalesTransaction)
        results = session.exec(statement).all()

        if not results:
            return pd.DataFrame()

        data_dicts = []
        for tx in results:
            data_dicts.append({
                "OrderID": tx.order_id,
                "CustomerID": tx.customer_id,
                "Product": tx.product_name,
                "Category": tx.category,
                "UnitPrice": tx.price,
                "Units": tx.quantity_sold,
                "Revenue": tx.total_sales,
                "Date": tx.order_date,
                "PaymentMethod": tx.payment_method,
                "CustomerRating": tx.customer_rating,
                "Month": tx.month,
                "Year": tx.year,
                "Profit": tx.profit,
                "Discount": tx.discount,
                "CustomerSegment": tx.customer_segment,
                "Region": tx.region,
            })

        df = pd.DataFrame(data_dicts)
        return df


# ---------------------------------------------------------------------------
# Customer CSV Data Processing & Analytics Service Functions
# ---------------------------------------------------------------------------

def clean_and_process_customer_csv(
    df: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Cleans and normalizes a raw Customer DataFrame in a fault-tolerant manner.

    Args:
        df: Raw Pandas DataFrame loaded from Customer CSV.

    Returns:
        Tuple of (Cleaned DataFrame, Report dictionary).
    """
    total_raw_rows = len(df)
    if total_raw_rows == 0:
        empty_report = {
            "total_rows_received": 0,
            "processed_rows": 0,
            "skipped_rows": 0,
            "message": "Uploaded CSV contains no rows.",
        }
        return pd.DataFrame(), empty_report

    df = df.copy()

    raw_columns = [str(col).strip().replace('"', '').replace("'", '') for col in df.columns]
    df.columns = raw_columns

    cleaned_df = pd.DataFrame()

    for original_col in df.columns:
        norm_key = original_col.lower().strip()
        standard_name = CUSTOMER_COLUMN_ALIAS_MAP.get(norm_key, original_col)
        cleaned_df[standard_name] = df[original_col].copy()

    for num_col in ["TotalOrders", "TotalSpend", "AverageOrderValue", "CustomerRating"]:
        if num_col in cleaned_df.columns:
            num_str = (
                cleaned_df[num_col]
                .astype(str)
                .str.replace('"', "", regex=False)
                .str.replace("'", "", regex=False)
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            cleaned_df[num_col] = pd.to_numeric(num_str, errors="coerce")
        else:
            cleaned_df[num_col] = 0.0

    for text_col in ["CustomerID", "CustomerName", "CustomerSegment", "Region", "City", "CustomerStatus", "LoyaltyTier", "ChurnRisk", "PreferredPaymentMethod"]:
        if text_col in cleaned_df.columns:
            cleaned_df[text_col] = (
                cleaned_df[text_col]
                .fillna("Unassigned")
                .astype(str)
                .str.replace('"', "", regex=False)
                .str.replace("'", "", regex=False)
                .str.strip()
            )
        else:
            cleaned_df[text_col] = "Unassigned"

    if "JoinDate" in cleaned_df.columns:
        cleaned_df["JoinDate"] = pd.to_datetime(cleaned_df["JoinDate"], format="mixed", errors="coerce")

    valid_mask = cleaned_df["CustomerID"].notna() & (cleaned_df["CustomerID"] != "Unassigned")
    final_df = cleaned_df[valid_mask].copy()

    processed_rows = len(final_df)
    skipped_rows = total_raw_rows - processed_rows

    report = {
        "total_rows_received": total_raw_rows,
        "processed_rows": processed_rows,
        "skipped_rows": skipped_rows,
        "message": f"Customer CSV processed successfully. {processed_rows} valid rows ingested, {skipped_rows} skipped."
    }

    return final_df, report


def calculate_customer_metrics(df: pd.DataFrame) -> dict[str, Any]:
    """Calculates comprehensive quantitative customer KPIs over cleaned customer data.

    Calculations are 100% deterministic Pandas dataframe aggregations.

    Args:
        df: Cleaned Customer Pandas DataFrame.

    Returns:
        Dictionary of pre-computed customer summary metrics.
    """
    if df.empty:
        return {
            "total_customers": 0,
            "active_customers": 0,
            "churned_customers": 0,
            "churn_rate_pct": 0.0,
            "churn_risk_breakdown": {},
            "total_customer_spend": 0.0,
            "avg_spend_per_customer": 0.0,
            "avg_customer_rating": 0.0,
            "segment_breakdown": {},
            "region_breakdown": {},
            "loyalty_tier_breakdown": {},
        }

    total_customers = int(len(df))
    
    status_counts = df["CustomerStatus"].str.lower().value_counts().to_dict()
    churned_customers = int(status_counts.get("churned", 0) + status_counts.get("inactive", 0))
    active_customers = int(total_customers - churned_customers)
    churn_rate_pct = round((churned_customers / total_customers) * 100, 2) if total_customers > 0 else 0.0

    churn_risk_counts = df["ChurnRisk"].value_counts().to_dict()
    total_spend = float(df["TotalSpend"].sum())
    avg_spend = round(float(df["TotalSpend"].mean()), 2) if total_customers > 0 else 0.0
    avg_rating = round(float(df["CustomerRating"].mean()), 2) if "CustomerRating" in df.columns and not df["CustomerRating"].isna().all() else 0.0

    segment_agg = df.groupby("CustomerSegment")["TotalSpend"].agg(["count", "sum"])
    segment_agg.columns = ["customers", "total_spend"]
    segment_breakdown = segment_agg.round(2).to_dict(orient="index")

    region_agg = df.groupby("Region")["TotalSpend"].agg(["count", "sum"])
    region_agg.columns = ["customers", "total_spend"]
    region_breakdown = region_agg.round(2).to_dict(orient="index")

    loyalty_breakdown = df["LoyaltyTier"].value_counts().to_dict()

    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "churned_customers": churned_customers,
        "churn_rate_pct": churn_rate_pct,
        "churn_risk_breakdown": churn_risk_counts,
        "total_customer_spend": round(total_spend, 2),
        "avg_spend_per_customer": avg_spend,
        "avg_customer_rating": avg_rating,
        "segment_breakdown": segment_breakdown,
        "region_breakdown": region_breakdown,
        "loyalty_tier_breakdown": loyalty_breakdown,
    }


def persist_customer_data_to_db(
    clean_df: pd.DataFrame,
    metrics: dict[str, Any]
) -> str:
    """Persists cleaned customer records and summary metrics into DB using SQLModel."""
    init_db()

    batch_id = f"customer_batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    with Session(engine) as session:
        records = []
        for _, row in clean_df.iterrows():
            join_dt = row.get("JoinDate")
            if pd.isna(join_dt):
                join_dt = None
            else:
                join_dt = pd.to_datetime(join_dt).to_pydatetime()

            rec = CustomerRecord(
                batch_id=batch_id,
                customer_id=str(row.get("CustomerID", "C0000")),
                customer_name=str(row.get("CustomerName", "Unassigned")),
                customer_segment=str(row.get("CustomerSegment", "Unassigned")),
                region=str(row.get("Region", "Unassigned")),
                city=str(row.get("City", "Unassigned")),
                join_date=join_dt,
                customer_status=str(row.get("CustomerStatus", "Active")),
                loyalty_tier=str(row.get("LoyaltyTier", "Standard")),
                customer_rating=float(row.get("CustomerRating", 0.0)),
                churn_risk=str(row.get("ChurnRisk", "Low")),
                preferred_payment_method=str(row.get("PreferredPaymentMethod", "Unknown")),
                total_orders=float(row.get("TotalOrders", 0.0)),
                total_spend=float(row.get("TotalSpend", 0.0)),
                average_order_value=float(row.get("AverageOrderValue", 0.0)),
            )
            records.append(rec)

        session.add_all(records)

        summary = CustomerAnalyticsSummary(
            batch_id=batch_id,
            metrics=metrics
        )
        session.add(summary)

        session.commit()

    return batch_id


def get_latest_customer_records_df() -> pd.DataFrame:
    """Queries stored CustomerRecord SQLModel records from DB and loads into a clean Pandas DataFrame."""
    init_db()

    with Session(engine) as session:
        statement = select(CustomerRecord)
        results = session.exec(statement).all()

        if not results:
            return pd.DataFrame()

        data_dicts = []
        for rec in results:
            data_dicts.append({
                "CustomerID": rec.customer_id,
                "CustomerName": rec.customer_name,
                "CustomerSegment": rec.customer_segment,
                "Region": rec.region,
                "City": rec.city,
                "JoinDate": rec.join_date,
                "CustomerStatus": rec.customer_status,
                "LoyaltyTier": rec.loyalty_tier,
                "CustomerRating": rec.customer_rating,
                "ChurnRisk": rec.churn_risk,
                "PreferredPaymentMethod": rec.preferred_payment_method,
                "TotalOrders": rec.total_orders,
                "TotalSpend": rec.total_spend,
                "AverageOrderValue": rec.average_order_value,
            })

        return pd.DataFrame(data_dicts)
