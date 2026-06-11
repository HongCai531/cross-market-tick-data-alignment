import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm

# 匯入自定義模組
from src.data_loader import RefinitivEngine
from src.lead_lag_engine import LeadLagEngine
from src.visualizer import plot_dual_axis_analysis

def main():
    print("--- 🚀 啟動跨市場高頻風險研究系統 ---")
    
    # 1. 初始化引擎與實驗設定
    engine = RefinitivEngine()
    
    # 定義測試矩陣：壓力日、基準日、事件日
    target_days = {
        "STRESS_0120": "2026-01-20",    # 格陵蘭關稅震撼 (SPY -2%)
        "BASELINE_0127": "2026-01-27",  # 歷史新高平穩日
        "EVENT_0128": "2026-01-28"      # FOMC 利率會議
    }
    
    market_start = datetime.strptime("14:30:00", "%H:%M:%S")
    market_end = datetime.strptime("21:00:00", "%H:%M:%S")
    chunk_minutes = 30
    
    os.makedirs('data', exist_ok=True)

    # 2. 開始多日循環分析
    for mode, target_date in target_days.items():
        print(f"\n📅 正在分析模式: {mode} (日期: {target_date})")
        
        all_results = []
        current_start = market_start
        total_steps = int((market_end - market_start).total_seconds() / 60) // chunk_minutes
        pbar = tqdm(total=total_steps, desc=f"📊 {mode} 進度", unit="chunk")

        while current_start < market_end:
            current_end = current_start + timedelta(minutes=chunk_minutes)
            start_ts = f"{target_date}T{current_start.strftime('%H:%M:%S')}Z"
            end_ts = f"{target_date}T{current_end.strftime('%H:%M:%S')}Z"
            chunk_label = f"{target_date}_{current_start.strftime('%H%M')}"

            spy_path = f"data/SPY_{chunk_label}.csv"
            tw_path = f"data/TAIEX_{chunk_label}.csv"

            try:
                # A. 數據抓取與快取機制
                if not os.path.exists(spy_path) or not os.path.exists(tw_path):
                    df_spy = engine.get_tick_data("SPY.P", start_ts, end_ts)
                    df_tw = engine.get_tick_data("TXc1", start_ts, end_ts)
                    if df_spy is not None: df_spy.to_csv(spy_path)
                    if df_tw is not None: df_tw.to_csv(tw_path)

                # B. 計量經濟學分析 (Lead-Lag & ADF)
                ll_engine = LeadLagEngine(spy_path, tw_path)
                temp_df = ll_engine.align_data() # 假設這是你對齊的函式
                print(f"DEBUG: 對齊後的原始數據量: {len(temp_df)}")
                # 取得平穩化後的對數收益率數據 (Log Returns)
                aligned_df, is_stationary = ll_engine.get_stationary_returns()
                
                if is_stationary:
                    # 計算相對價差 (Relative Spread)
                    aligned_df['rel_spread'] = (aligned_df['ask_tw'] - aligned_df['bid_tw']) / aligned_df['mid_price_tw']
                    avg_spread = aligned_df['rel_spread'].mean()
                    
                    # 計算領先落後相關性
                    lags = ll_engine.calculate_correlation(aligned_df)
                    best_lag = max(lags, key=lags.get)
                    max_corr = lags[best_lag]

                    all_results.append({
                        "time": current_start.strftime('%H:%M'),
                        "lag": best_lag,
                        "corr": max_corr,
                        "avg_spread": avg_spread
                    })
            except Exception as e:
                # 不要只寫 pass，要把錯誤印出來
                print(f"❌ 偵錯點 - 時段 {current_start.strftime('%H:%M')} 出錯: {e}")

            pbar.update(1)
            current_start = current_end
        
        pbar.close()
        print(f"DEBUG: {mode} 收集到的有效時段數量: {len(all_results)}")
        # 3. 風險指標計算 (L-VaR Modeling)
        if all_results:
            summary_df = pd.DataFrame(all_results)
            z_score = 1.645 # 95% Confidence Level
            
            # L-VaR = Standard VaR + (Spread / 2)
            summary_df['standard_var'] = z_score * 0.01 
            summary_df['l_var'] = summary_df['standard_var'] + (summary_df['avg_spread'] / 2)
            summary_df['add_on_pct'] = (summary_df['l_var'] - summary_df['standard_var']) / summary_df['standard_var'] * 100
            
            # 存檔並繪圖
            output_csv = f"data/summary_{mode}.csv"
            summary_df.to_csv(output_csv, index=False)
            print(f"✅ {mode} 分析完成。Avg Add-on: {summary_df['add_on_pct'].mean():.4f}%")
            
            # 生成該日期的雙軸圖表
            plot_dual_axis_analysis(output_csv, title=f"Risk Analysis: {mode} ({target_date})")
        else:
            print(f"❌ 警告: {mode} 沒有任何時段通過檢定，請檢查 is_stationary 邏輯或數據完整性。")

    print("\n--- ✨ 所有實驗組分析完畢 ---")

if __name__ == "__main__":
    main()