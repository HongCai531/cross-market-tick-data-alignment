# Cross market tick data time alignment automation

This project provides a simple Python workflow for aligning TAIEX and SPY tick data by timestamp.

It is designed to support lead-lag analysis between the Taiwan futures market and the U.S. equity market.

## Project Structure

```text
TAIEX_Quant_Project/
├── data/                  # Input and output CSV files
├── src/                   # Core Python logic
│   └── lead_lag_engine.py # Data loading and timestamp alignment engine
├── align_tick_data.py     # Command-line version
├── run_align.py           # Simple one-click version for non-technical users
├── requirements.txt       # Python dependencies
└── README.md
