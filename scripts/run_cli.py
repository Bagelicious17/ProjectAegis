"""
CLI entrypoint for running the Aegis Due Diligence Swarm.

Usage:
    python scripts/run_cli.py
"""

import sys
import os

# Add project root to path so 'src' package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import validate_api_keys, logger
from src.crews import run_aegis_analysis


def main():
    """Run the Aegis Swarm via interactive CLI prompts."""
    print("🛡️  Aegis Due Diligence Swarm — CLI Mode")
    print("=" * 50)

    if not validate_api_keys():
        sys.exit(1)

    company_name = (
        input("Enter target company name (default: Boeing): ").strip() or "Boeing"
    )
    csv_path = (
        input("Enter CSV path (default: data/financial_data.csv): ").strip()
        or "data/financial_data.csv"
    )

    print(f"\n🚀 Deploying Aegis Swarm for '{company_name}'...")
    result = run_aegis_analysis(company_name, csv_path)

    if result["success"]:
        print("\n" + "=" * 50)
        print("✅ FINAL AEGIS REPORT:")
        print("=" * 50)
        print(result["report"])
    else:
        print("\n" + "=" * 50)
        print("❌ ANALYSIS FAILED:")
        print("=" * 50)
        print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
