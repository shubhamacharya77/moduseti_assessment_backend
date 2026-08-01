import os
from typing import Any
import pandas as pd
from models.evidence import EvidenceItem
from services.csv_service import (
    calculate_customer_metrics,
    clean_and_process_customer_csv,
    get_latest_customer_records_df,
)


class CustomerAnalyticsTool:
    """Independent quantitative tool for customer analytics and churn risk metrics retrieval."""

    def __init__(self, csv_filepath: str = "customers.csv"):
        self.csv_filepath = csv_filepath

    def _get_customer_dataframe(self) -> pd.DataFrame:
        """Retrieves customer DataFrame from DB or falls back to local CSV file."""
        df = get_latest_customer_records_df()
        if not df.empty:
            return df

        if os.path.exists(self.csv_filepath):
            raw_df = pd.read_csv(self.csv_filepath)
            clean_df, _ = clean_and_process_customer_csv(raw_df)
            return clean_df

        return pd.DataFrame()

    def get_summary_metrics(self) -> list[EvidenceItem]:
        """Calculates executive customer summary KPIs and returns a list of EvidenceItem objects.

        Returns:
            List containing normalized EvidenceItem object.
        """
        df = self._get_customer_dataframe()
        metrics = calculate_customer_metrics(df)

        item = EvidenceItem(
            source="Customer Analytics Tool",
            category="Quantitative Metric",
            title="Executive Customer Health & Churn Risk Summary",
            details=metrics,
            confidence="High (100% Deterministic Python Calculation)",
        )
        return [item]
