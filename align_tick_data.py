import argparse
from pathlib import Path

from src.lead_lag_engine import LeadLagEngine


def parse_args():
    parser = argparse.ArgumentParser(
        description="Align TAIEX and S&P 500/SPY tick CSV files by Timestamp."
    )
    parser.add_argument("--taiex", required=True, help="TAIEX tick CSV path")
    parser.add_argument("--sp500", required=True, help="S&P 500/SPY tick CSV path")
    parser.add_argument("--output", required=True, help="Aligned CSV output path")
    parser.add_argument(
        "--direction",
        choices=["backward", "forward", "nearest"],
        default="backward",
        help="pandas merge_asof direction. backward avoids using future SPY ticks.",
    )
    parser.add_argument(
        "--tolerance",
        default=None,
        help="Maximum allowed time gap, for example 100ms, 1s, or 5min.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    engine = LeadLagEngine(
        spy_path=args.sp500,
        taiex_path=args.taiex,
        tolerance=args.tolerance,
        direction=args.direction,
    )
    aligned = engine.align_data()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    aligned.to_csv(output_path, index_label="Timestamp")

    print(f"完成: {output_path}")
    print(f"對齊後筆數: {len(aligned)}")
    if not aligned.empty:
        print(f"時間範圍: {aligned.index.min()} -> {aligned.index.max()}")


if __name__ == "__main__":
    main()
