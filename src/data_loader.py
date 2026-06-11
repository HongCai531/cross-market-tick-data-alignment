import refinitiv.data as rd
import pandas as pd

class RefinitivEngine:
    def __init__(self):
        # 啟動時自動連接 Workspace
        rd.open_session()


    def get_tick_data(self, ric, start, end):
        df = rd.get_history(universe=ric, interval="5min", start=start, end=end)
        
        if df is not None and not df.empty:
            # 1. 先去除完全重複的原始欄位名
            df = df.loc[:, ~df.columns.duplicated()]

            # 2. 定義你的環境專屬映射表
            rename_map = {
                'TRDPRC_1': 'price',
                'TRDVOL_1': 'volume',
                'BID': 'bid',
                'ASK': 'ask',
                'BIDSIZE': 'bid_size', # 你確認的欄位名
                'ASKSIZE': 'ask_size'  # 你確認的欄位名
            }
            
            # 3. 執行重新命名
            df = df.rename(columns=rename_map)

            # 4. 再次去重（防止改名後出現重複）
            df = df.loc[:, ~df.columns.duplicated()]

            # 5. 只保留這 6 個核心變量，其餘雜訊全部刪除
            keep_cols = ['price', 'volume', 'bid', 'ask', 'bid_size', 'ask_size']
            df = df[[c for c in keep_cols if c in df.columns]]
            
            # 6. 計算中間價 (Mid-price)
            # 公式： $$Mid\text{-}Price = \frac{Bid + Ask}{2}$$
            if 'bid' in df.columns and 'ask' in df.columns:
                df['mid_price'] = (df['bid'].astype(float) + df['ask'].astype(float)) / 2
                
            return df
        return None