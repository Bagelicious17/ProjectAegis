"""Custom tool for fetching live financial data from Yahoo Finance."""

import logging

from crewai.tools import tool

logger = logging.getLogger("aegis.tools.yahoo")


@tool("Fetch Live Stock Data")
def fetch_yahoo_finance(ticker: str) -> str:
    """Fetches real-time financial data from Yahoo Finance for a publicly traded company.

    Retrieves key financial metrics including stock price, market cap,
    revenue, earnings, and key ratios. Use this when the user provides
    a stock ticker symbol instead of a CSV file.

    Args:
        ticker: The stock ticker symbol (e.g., 'AAPL', 'BA', 'TSLA').

    Returns:
        A formatted string containing the company's financial overview,
        key metrics, and quarterly financial trends.
    """
    try:
        import yfinance as yf

        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or "shortName" not in info:
            return f"Error: Could not find data for ticker '{ticker}'. Please verify the symbol."

        # --- Company Overview ---
        overview = (
            f"Company: {info.get('shortName', 'N/A')} ({ticker.upper()})\n"
            f"Sector: {info.get('sector', 'N/A')}\n"
            f"Industry: {info.get('industry', 'N/A')}\n"
            f"Country: {info.get('country', 'N/A')}\n"
            f"Employees: {info.get('fullTimeEmployees', 'N/A'):,}\n"
        )

        # --- Key Financial Metrics ---
        metrics = (
            f"\n--- Key Financial Metrics ---\n"
            f"Market Cap: ${info.get('marketCap', 0):,.0f}\n"
            f"Current Price: ${info.get('currentPrice', info.get('previousClose', 0)):.2f}\n"
            f"52-Week High: ${info.get('fiftyTwoWeekHigh', 0):.2f}\n"
            f"52-Week Low: ${info.get('fiftyTwoWeekLow', 0):.2f}\n"
            f"Revenue (TTM): ${info.get('totalRevenue', 0):,.0f}\n"
            f"Net Income (TTM): ${info.get('netIncomeToCommon', 0):,.0f}\n"
            f"Total Debt: ${info.get('totalDebt', 0):,.0f}\n"
            f"Total Cash: ${info.get('totalCash', 0):,.0f}\n"
            f"Debt-to-Equity: {info.get('debtToEquity', 'N/A')}\n"
            f"Profit Margin: {info.get('profitMargins', 0):.2%}\n"
            f"Operating Margin: {info.get('operatingMargins', 0):.2%}\n"
            f"Return on Equity: {info.get('returnOnEquity', 0):.2%}\n"
            f"P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
            f"Forward P/E: {info.get('forwardPE', 'N/A')}\n"
        )

        # --- Quarterly Financials ---
        quarterly_section = ""
        try:
            quarterly = stock.quarterly_financials
            if quarterly is not None and not quarterly.empty:
                # Show last 4 quarters
                quarterly_section = f"\n--- Quarterly Financials (Last 4 Quarters) ---\n"
                for col in quarterly.columns[:4]:
                    quarter_label = col.strftime("%Y-Q%q") if hasattr(col, "strftime") else str(col)
                    quarterly_section += f"\n{quarter_label}:\n"
                    for metric in ["Total Revenue", "Net Income", "Operating Income", "Gross Profit"]:
                        if metric in quarterly.index:
                            val = quarterly.loc[metric, col]
                            quarterly_section += f"  {metric}: ${val:,.0f}\n"
        except Exception:
            quarterly_section = "\n(Quarterly financial data not available)\n"

        # --- Analyst Recommendations ---
        recommendations_section = ""
        try:
            rec = info.get("recommendationKey", "N/A")
            rec_mean = info.get("recommendationMean", "N/A")
            target_high = info.get("targetHighPrice", "N/A")
            target_low = info.get("targetLowPrice", "N/A")
            target_mean = info.get("targetMeanPrice", "N/A")
            recommendations_section = (
                f"\n--- Analyst Consensus ---\n"
                f"Recommendation: {rec}\n"
                f"Mean Score: {rec_mean} (1=Strong Buy, 5=Sell)\n"
                f"Price Target: ${target_low} - ${target_high} (mean: ${target_mean})\n"
            )
        except Exception:
            pass

        return f"--- Company Overview ---\n{overview}{metrics}{quarterly_section}{recommendations_section}"

    except ImportError:
        return (
            "Error: yfinance library is not installed. "
            "Install it with: pip install yfinance"
        )
    except Exception as e:
        return f"Error fetching data for '{ticker}': {str(e)}"
