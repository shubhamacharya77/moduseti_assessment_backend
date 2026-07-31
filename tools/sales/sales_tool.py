import os
from typing import Any
import pandas as pd
from models.evidence import EvidenceItem
from services.csv_service import (
    calculate_sales_metrics,
    clean_and_process_sales_csv,
    get_latest_sales_transactions_df,
    query_sales_analytics,
)


class SalesAnalyticsTool:
    """Independent quantitative tool for sales metrics retrieval and dynamic slice aggregations."""

    def __init__(self, csv_filepath: str = "sales_transactions.csv"):
        self.csv_filepath = csv_filepath

    def _get_sales_dataframe(self) -> pd.DataFrame:
        """Retrieves sales transactions DataFrame from DB or falls back to local CSV file."""
        df = get_latest_sales_transactions_df()
        if not df.empty:
            return df

        if os.path.exists(self.csv_filepath):
            raw_df = pd.read_csv(self.csv_filepath)
            clean_df, _ = clean_and_process_sales_csv(raw_df)
            return clean_df

        return pd.DataFrame()

    def get_summary_metrics(self) -> list[EvidenceItem]:
        """Calculates executive sales summary KPIs and returns a list of EvidenceItem objects.

        Returns:
            List containing normalized EvidenceItem object.
        """
        df = self._get_sales_dataframe()
        metrics = calculate_sales_metrics(df)

        item = EvidenceItem(
            source="Sales Analytics Tool",
            category="Quantitative Metric",
            title="Executive Sales Performance Summary",
            details=metrics,
            confidence="High (100% Deterministic Python Calculation)",
        )
        return [item]

    def query_slice(
        self,
        category: str | None = None,
        region: str | None = None,
        segment: str | None = None,
        product: str | None = None
    ) -> list[EvidenceItem]:
        """Runs on-the-fly dynamic slice aggregation over sales records.

        Args:
            category: Optional category filter.
            region: Optional region filter.
            segment: Optional customer segment filter.
            product: Optional product filter.

        Returns:
            List containing normalized EvidenceItem for the requested sales slice.
        """
        df = self._get_sales_dataframe()
        slice_res = query_sales_analytics(
            df=df,
            product=product,
            category=category,
            region=region,
            segment=segment
        )

        filter_desc = ", ".join([f"{k}='{v}'" for k, v in slice_res.get("filters_applied", {}).items() if v])
        title_str = f"Sales Performance Slice ({filter_desc})" if filter_desc else "Sales Performance Slice (All Records)"

        item = EvidenceItem(
            source="Sales Analytics Tool (Dynamic Query)",
            category="Quantitative Metric",
            title=title_str,
            details=slice_res,
            confidence="High (100% Deterministic Python Dynamic Query)",
        )
        return [item]
