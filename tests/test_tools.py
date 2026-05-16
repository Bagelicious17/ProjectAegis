"""Unit tests for the custom financial CSV analysis tool."""

import os
import sys
import csv
import tempfile

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.financial_csv import analyze_financial_csv


@pytest.fixture
def sample_csv(tmp_path):
    """Create a temporary CSV file with sample financial data."""
    csv_file = tmp_path / "test_financials.csv"
    data = [
        ["Quarter", "Revenue_Millions", "Operating_Costs_Millions", "Debt_Millions"],
        ["Q1_2023", "1000", "800", "200"],
        ["Q2_2023", "1200", "850", "180"],
        ["Q3_2023", "900", "900", "250"],
    ]
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return str(csv_file)


@pytest.fixture
def empty_csv(tmp_path):
    """Create an empty CSV file (headers only)."""
    csv_file = tmp_path / "empty.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Quarter", "Revenue"])
    return str(csv_file)


class TestAnalyzeFinancialCSV:
    """Tests for the analyze_financial_csv tool."""

    def test_returns_summary_sections(self, sample_csv):
        """Tool output should contain all three analysis sections."""
        result = analyze_financial_csv.run(file_path=sample_csv)
        assert "Statistical Summary" in result
        assert "Trend Analysis" in result
        assert "Most Recent Data Snapshot" in result

    def test_trend_calculation(self, sample_csv):
        """Trend percentages should be calculated correctly."""
        result = analyze_financial_csv.run(file_path=sample_csv)
        # Revenue went from 1000 to 900 = -10%
        assert "-10.00%" in result
        # Debt went from 200 to 250 = 25%
        assert "25.00%" in result

    def test_nonexistent_file_returns_error(self):
        """Should return an error message for missing files, not crash."""
        result = analyze_financial_csv.run(file_path="nonexistent.csv")
        assert "Error reading CSV" in result

    def test_handles_empty_data(self, empty_csv):
        """Should handle a CSV with only headers gracefully."""
        result = analyze_financial_csv.run(file_path=empty_csv)
        # Should not crash — may return summary or error depending on pandas behavior
        assert isinstance(result, str)
