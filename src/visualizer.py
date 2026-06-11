import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_dual_axis_analysis(csv_path="data/daily_lead_lag_summary.csv"):
    df = pd.read_csv(csv_path)
    
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax1 = plt.subplots(figsize=(14, 7))

    # 1. 繪製相關係數 (左軸)
    color_corr = '#1f77b4'
    ax1.set_xlabel('Time (UTC)')
    ax1.set_ylabel('Correlation Coefficient (ρ)', color=color_corr, fontsize=12, fontweight='bold')
    sns.lineplot(x='time', y='corr', data=df, marker='o', color=color_corr, linewidth=2.5, ax=ax1, label='Correlation')
    ax1.tick_params(axis='y', labelcolor=color_corr)
    ax1.set_ylim(0, 1.0) # 這次我們看全範圍

    # 2. 建立第二條 Y 軸 (右軸) 繪製價差
    ax2 = ax1.twinx() 
    color_spread = '#e31a1c'
    ax2.set_ylabel('Avg Relative Spread (Liquidity Cost)', color=color_spread, fontsize=12, fontweight='bold')
    sns.lineplot(x='time', y='avg_spread', data=df, marker='s', color=color_spread, linewidth=2, linestyle='--', ax=ax2, label='Spread')
    ax2.tick_params(axis='y', labelcolor=color_spread)

    # 3. 圖表美化
    plt.title('Market Synchronization vs. Liquidity Risk (Jan 20, 2026)', fontsize=16, fontweight='bold', pad=25)
    
    # 合併兩個軸的圖例
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper left')

    # 設定 X 軸標籤旋轉
    ax1.set_xticks(range(len(df['time'])))
    ax1.set_xticklabels(df['time'], rotation=45)
    
    plt.tight_layout()
    plt.savefig("data/dual_risk_analysis.png", dpi=300)
    print("✅ 雙軸分析圖表已儲存至: data/dual_risk_analysis.png")
    plt.show()

if __name__ == "__main__":
    plot_dual_axis_analysis()