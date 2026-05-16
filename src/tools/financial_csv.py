"""Custom Pandas tool for reading and analyzing financial CSV data."""

import pandas as pd
from crewai.tools import tool


@tool("Read Financial Data")
def analyze_financial_csv(file_path: str) -> str:
    """Reads a CSV file containing financial data and returns a statistical
    summary, trend analysis, and the most recent data snapshot.

    Args:
        file_path: Path to the CSV file to analyze.

    Returns:
        A formatted string containing statistical summary, trend analysis,
        and the most recent row of data.
    """
    try:
        df = pd.read_csv(file_path)

        # Statistical summary via Pandas describe()
        summary = df.describe().to_string()

        # Compute overall trend (percentage change from first to last period)
        numeric_cols = df.select_dtypes(include=["number"]).columns
        trends = "Overall Changes (First to Last Row):\n"
        for col in numeric_cols:
            start_val = df[col].iloc[0]
            end_val = df[col].iloc[-1]
            if start_val != 0:
                pct_change = ((end_val - start_val) / start_val) * 100
                trends += f"- {col}: {pct_change:.2f}% (from {start_val} to {end_val})\n"

        # Most recent quarter snapshot
        recent_status = df.iloc[-1].to_string()

        return (
            f"--- Statistical Summary ---\n{summary}\n\n"
            f"--- Trend Analysis ---\n{trends}\n\n"
            f"--- Most Recent Data Snapshot ---\n{recent_status}"
        )
    except Exception as e:
        return f"Error reading CSV: {str(e)}"
