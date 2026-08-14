# Codigó principal para análisis de volatilidad de divisas usando Yahoo Finance.

import yfinance as yf
import pandas as pd
import numpy as np
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Optional
import warnings

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)


# ─── Pares de divisas más comunes ───────────────────────────────────────────
FOREX_PAIRS = {
    "EURUSD": "EUR/USD - Euro / Dólar Americano",
    "GBPUSD": "GBP/USD - Libra Esterlina / Dólar Americano",
    "USDJPY": "USD/JPY - Dólar Americano / Yen Japonés",
    "USDCHF": "USD/CHF - Dólar Americano / Franco Suizo",
    "AUDUSD": "AUD/USD - Dólar Australiano / Dólar Americano",
    "USDCAD": "USD/CAD - Dólar Americano / Dólar Canadiense",
    "NZDUSD": "NZD/USD - Dólar Neozelandés / Dólar Americano",
    "USDMXN": "USD/MXN - Dólar Americano / Peso Mexicano",
    "USDCOP": "USD/COP - Dólar Americano / Peso Colombiano",
    "USDBRL": "USD/BRL - Dólar Americano / Real Brasileño",
    "USDCLP": "USD/CLP - Dólar Americano / Peso Chileno",
    "USDARS": "USD/ARS - Dólar Americano / Peso Argentino",
}

PERIODS = {
    "1w": {"days": 7, "label": "1 Semana"},
    "1m": {"days": 30, "label": "1 Mes"},
    "3m": {"days": 90, "label": "3 Meses"},
    "6m": {"days": 180, "label": "6 Meses"},
    "1y": {"days": 365, "label": "1 Año"},
    "2y": {"days": 730, "label": "2 Años"},
}


class ForexVolatilityAnalyzer:
    """
    Analiza la volatilidad de pares de divisas usando datos de Yahoo Finance.

    Métricas calculadas:
    - Volatilidad histórica (desviación estándar de retornos logarítmicos)
    - Volatilidad anualizada
    - ATR - Average True Range
    - Bandas de Bollinger
    - Retornos acumulados
    - Drawdown máximo
    - Indicadores Técnicos (opcional): SMA, EMA, RSI, MACD
    """

    def __init__(self, annualization_factor: int = 252):
        self.annualization_factor = annualization_factor

    def _get_ticker(self, pair: str) -> str:
        pair = pair.upper().replace("/", "").replace("-", "")
        return f"{pair}=X"

    def fetch_data(
        self,
        pair: str,
        period: str = "3m",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        ticker = self._get_ticker(pair)

        if start_date and end_date:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        else:
            if period not in PERIODS:
                raise ValueError(
                    f"Período '{period}' no válido. Usa: {list(PERIODS.keys())}"
                )
            days = PERIODS[period]["days"]
            end = datetime.today()
            start = end - timedelta(days=days)
            df = yf.download(ticker, start=start, end=end, progress=False)

        if df.empty:
            raise ValueError(f"No se obtuvieron datos para '{pair}'.")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index = pd.to_datetime(df.index)
        return df.dropna()

    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        result = df.copy()
        result["log_return"] = np.log(result["Close"] / result["Close"].shift(1))
        result["volatility_daily"] = result["log_return"].rolling(window=window).std()
        result["volatility_annual"] = result["volatility_daily"] * np.sqrt(
            self.annualization_factor
        )
        result["cumulative_return"] = (1 + result["log_return"]).cumprod() - 1

        result["tr1"] = result["High"] - result["Low"]
        result["tr2"] = (result["High"] - result["Close"].shift(1)).abs()
        result["tr3"] = (result["Low"] - result["Close"].shift(1)).abs()
        result["true_range"] = result[["tr1", "tr2", "tr3"]].max(axis=1)
        result["atr"] = result["true_range"].rolling(window=window).mean()
        result.drop(columns=["tr1", "tr2", "tr3"], inplace=True)

        result["bb_mid"] = result["Close"].rolling(window=window).mean()
        bb_std = result["Close"].rolling(window=window).std()
        result["bb_upper"] = result["bb_mid"] + 2 * bb_std
        result["bb_lower"] = result["bb_mid"] - 2 * bb_std
        result["bb_width"] = (result["bb_upper"] - result["bb_lower"]) / result[
            "bb_mid"
        ]

        rolling_max = result["Close"].cummax()
        result["drawdown"] = (result["Close"] - rolling_max) / rolling_max

        return result

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        result = df.copy()
        close = result["Close"]

        for window in [20, 50, 200]:
            result[f"sma_{window}"] = close.rolling(window=window).mean()
            result[f"ema_{window}"] = close.ewm(span=window, adjust=False).mean()

        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        result["rsi"] = 100 - (100 / (1 + rs))

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        result["macd"] = ema12 - ema26
        result["macd_signal"] = result["macd"].ewm(span=9, adjust=False).mean()
        result["macd_hist"] = result["macd"] - result["macd_signal"]

        return result

    def analyze(
        self,
        pair: str,
        period: str = "3m",
        window: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_indicators: bool = False,
    ) -> "VolatilityReport":
        logger.info(f"Descargando datos para {pair}...")
        df = self.fetch_data(pair, period, start_date, end_date)
        logger.info(
            f"{len(df)} registros obtenidos ({df.index[0].date()} → {df.index[-1].date()})"
        )

        logger.info("Calculando métricas de volatilidad...")
        metrics_df = self.calculate_volatility(df, window=window)

        if include_indicators:
            logger.info("Calculando indicadores técnicos...")
            metrics_df = self.calculate_technical_indicators(metrics_df)

        return VolatilityReport(
            pair=pair, period=period, window=window, data=metrics_df
        )

    def compare_pairs(
        self,
        pairs: list[str],
        period: str = "3m",
        window: int = 20,
    ) -> pd.DataFrame:
        results = []

        def _analyze_pair(pair):
            try:
                report = self.analyze(pair, period, window)
                return report.get_summary_dict()
            except Exception as e:
                logger.error(f"Error en {pair}: {e}")
                return None

        with ThreadPoolExecutor() as executor:
            future_to_pair = {
                executor.submit(_analyze_pair, pair): pair for pair in pairs
            }
            for future in as_completed(future_to_pair):
                res = future.result()
                if res:
                    results.append(res)

        if not results:
            raise ValueError("No se pudo obtener datos para ningún par.")

        df = pd.DataFrame(results).set_index("pair")
        return df.sort_values("volatility_annual_pct", ascending=False)



class VolatilityReport:
    def __init__(self, pair: str, period: str, window: int, data: pd.DataFrame):
        self.pair = pair.upper()
        self.period = period
        self.window = window
        self.data = data
        self._last = data.iloc[-1]

    def _fmt(self, value, fmt=".5f") -> str:
        """Formatea un valor, devolviendo 'N/A' si es NaN."""
        if pd.isna(value):
            return "N/A"
        try:
            return f"{value:{fmt}}"
        except (ValueError, TypeError):
            return str(value)

    def summary(self) -> str:
        d = self._last
        start = self.data.index[0].strftime("%Y-%m-%d")
        end = self.data.index[-1].strftime("%Y-%m-%d")
        total_return = self.data["cumulative_return"].iloc[-1] * 100
        max_dd = self.data["drawdown"].min() * 100

        lines = [
            f"\n{'═' * 55}",
            f"   ANÁLISIS DE VOLATILIDAD — {self.pair}",
            f"{'═' * 55}",
            f"  Período analizado : {start} → {end}",
            f"  Ventana (window)  : {self.window} días",
            f"{'─' * 55}",
            f"  Precio actual     : {self._fmt(d['Close'])}",
            f"  Retorno total     : {self._fmt(total_return, '+.2f')}%",
            f"  Drawdown máximo   : {self._fmt(max_dd, '.2f')}%",
            f"{'─' * 55}",
            f"  Volatilidad diaria  (rolling {self.window}d) : {self._fmt(d['volatility_daily'] * 100, '.3f')}%",
            f"  Volatilidad anual   (rolling {self.window}d) : {self._fmt(d['volatility_annual'] * 100, '.2f')}%",
            f"  ATR ({self.window}d)                         : {self._fmt(d['atr'])}",
            f"{'─' * 55}",
            f"  Banda Bollinger Superior : {self._fmt(d['bb_upper'])}",
            f"  Banda Bollinger Media    : {self._fmt(d['bb_mid'])}",
            f"  Banda Bollinger Inferior : {self._fmt(d['bb_lower'])}",
            f"  Ancho Bandas (BB Width)  : {self._fmt(d['bb_width'] * 100, '.3f')}%",
            f"{'═' * 55}\n",
        ]
        return "\n".join(lines)

    def get_summary_dict(self) -> dict:
        d = self._last
        return {
            "pair": self.pair,
            "price": round(float(d["Close"]), 5) if not pd.isna(d["Close"]) else None,
            "volatility_daily_pct": round(float(d["volatility_daily"]) * 100, 4) if not pd.isna(d["volatility_daily"]) else None,
            "volatility_annual_pct": round(float(d["volatility_annual"]) * 100, 2) if not pd.isna(d["volatility_annual"]) else None,
            "atr": round(float(d["atr"]), 5) if not pd.isna(d["atr"]) else None,
            "bb_width_pct": round(float(d["bb_width"]) * 100, 4) if not pd.isna(d["bb_width"]) else None,
            "cumulative_return_pct": round(float(self.data["cumulative_return"].iloc[-1]) * 100, 2) if not pd.isna(self.data["cumulative_return"].iloc[-1]) else None,
            "max_drawdown_pct": round(float(self.data["drawdown"].min()) * 100, 2) if not pd.isna(self.data["drawdown"].min()) else None,
            "n_observations": len(self.data),
        }
