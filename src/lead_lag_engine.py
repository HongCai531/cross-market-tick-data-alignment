import pandas as pd


class LeadLagEngine:
    """
    Read two tick CSV files and align them by timestamp.

    This class currently focuses only on the data automation part:
    1. read CSV files
    2. clean timestamps and numeric columns
    3. create/fill mid_price
    4. align TAIEX ticks with SPY ticks by time
    """

    def __init__(self, spy_path, taiex_path, tolerance=None, direction="backward"):
        self.spy_path = spy_path
        self.taiex_path = taiex_path
        self.tolerance = pd.Timedelta(tolerance) if tolerance else None
        self.direction = direction

        self.df_spy = self._load_tick_csv(spy_path, market="spy")
        self.df_taiex = self._load_tick_csv(taiex_path, market="taiex")
        self.aligned_df = None

    @staticmethod
    def _load_tick_csv(path, market):
        df = pd.read_csv(path, parse_dates=["Timestamp"])

        df = df.dropna(subset=["Timestamp"])
        df = df.drop_duplicates()
        df = df.set_index("Timestamp")
        df = df.sort_index()

        numeric_columns = [
            "price",
            "volume",
            "bid",
            "ask",
            "bid_size",
            "ask_size",
            "mid_price",
        ]
        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        df = LeadLagEngine._ensure_mid_price(df)
        df["source_market"] = market
        return df

    @staticmethod
    def _ensure_mid_price(df):
        if "mid_price" not in df.columns:
            df["mid_price"] = pd.NA

        if {"bid", "ask"}.issubset(df.columns):
            bid_ask_mid = (df["bid"] + df["ask"]) / 2
            df["mid_price"] = df["mid_price"].fillna(bid_ask_mid)

        if "price" in df.columns:
            df["mid_price"] = df["mid_price"].fillna(df["price"])

        return df

    def align_data(self):
        aligned = pd.merge_asof(
            self.df_taiex,
            self.df_spy,
            left_index=True,
            right_index=True,
            direction=self.direction,
            tolerance=self.tolerance,
            suffixes=("_taiex", "_spy"),
        )

        self.aligned_df = aligned.dropna(subset=["mid_price_taiex", "mid_price_spy"])
        return self.aligned_df
