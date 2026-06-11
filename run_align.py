from src.lead_lag_engine import LeadLagEngine

taiex_path = "data/test_TAIEX_sample.csv"
sp500_path = "data/test_SPY_sample.csv"
output_path = "data/aligned_sample1.csv"

engine = LeadLagEngine(
    spy_path=sp500_path,
    taiex_path=taiex_path,
    direction="backward",
    tolerance="1s",
)

aligned = engine.align_data()
aligned.to_csv(output_path, index_label="Timestamp")

print("Complete！")
print(f"Export file：{output_path}")
print(f"Aligned data points：{len(aligned)}")

if not aligned.empty:
    print(f"Time range：{aligned.index.min()} -> {aligned.index.max()}")