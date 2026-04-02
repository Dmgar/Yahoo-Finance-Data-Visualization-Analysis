#Codigó principal para análisis de volatilidad de divisas usando Yahoo Finance.

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
import warnings
warnings.filterwarnings("ignore")


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
    "1w":  {"days": 7,   "label": "1 Semana"},
    "1m":  {"days": 30,  "label": "1 Mes"},
    "3m":  {"days": 90,  "label": "3 Meses"},
    "6m":  {"days": 180, "label": "6 Meses"},
    "1y":  {"days": 365, "label": "1 Año"},
    "2y":  {"days": 730, "label": "2 Años"},
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

    Uso básico:
        analyzer = ForexVolatilityAnalyzer()
        result = analyzer.analyze("EURUSD", period="3m")
        print(result.summary())
    """

    def __init__(self, annualization_factor: int = 252):
        """
        Args:
            annualization_factor: Factor para anualizar volatilidad
                                  (252 días de trading por año)
        """
        self.annualization_factor = annualization_factor

    def _get_ticker(self, pair: str) -> str:
        """Convierte el par al formato de Yahoo Finance (ej: EURUSD → EURUSD=X)."""
        pair = pair.upper().replace("/", "").replace("-", "")
        return f"{pair}=X"

    def fetch_data(
        self,
        pair: str,
        period: str = "3m",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Descarga datos históricos de Yahoo Finance.

        Args:
            pair: Par de divisas (ej: 'EURUSD', 'USDCOP')
            period: Período predefinido ('1w', '1m', '3m', '6m', '1y', '2y')
            start_date: Fecha inicio personalizada (formato 'YYYY-MM-DD')
            end_date: Fecha fin personalizada (formato 'YYYY-MM-DD')

        Returns:
            DataFrame con columnas: Open, High, Low, Close, Volume

        Raises:
            ValueError: Si el par no se pudo descargar o está vacío
        """
        ticker = self._get_ticker(pair)

        if start_date and end_date:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
        else:
            if period not in PERIODS:
                raise ValueError(f"Período '{period}' no válido. Usa: {list(PERIODS.keys())}")
            days = PERIODS[period]["days"]
            end = datetime.today()
            start = end - timedelta(days=days)
            df = yf.download(ticker, start=start, end=end, progress=False)

        if df.empty:
            raise ValueError(
                f"No se obtuvieron datos para '{pair}'. "
                f"Verifica que el par sea válido (ej: EURUSD, USDCOP)."
            )

        # Aplanar columnas MultiIndex si existen
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.index = pd.to_datetime(df.index)
        return df.dropna()

    def calculate_volatility(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """
        Calcula múltiples métricas de volatilidad.

        Args:
            df: DataFrame con datos OHLCV
            window: Ventana de días para métricas móviles (default: 20)

        Returns:
            DataFrame con todas las métricas calculadas
        """
        result = df.copy()

        # Retornos logarítmicos
        result["log_return"] = np.log(result["Close"] / result["Close"].shift(1))

        # Volatilidad histórica (rolling)
        result["volatility_daily"] = result["log_return"].rolling(window=window).std()
        result["volatility_annual"] = result["volatility_daily"] * np.sqrt(self.annualization_factor)

        # Retorno acumulado 
        result["cumulative_return"] = (1 + result["log_return"]).cumprod() - 1

        # ATR - Average True Range
        result["tr1"] = result["High"] - result["Low"]
        result["tr2"] = (result["High"] - result["Close"].shift(1)).abs()
        result["tr3"] = (result["Low"] - result["Close"].shift(1)).abs()
        result["true_range"] = result[["tr1", "tr2", "tr3"]].max(axis=1)
        result["atr"] = result["true_range"].rolling(window=window).mean()
        result.drop(columns=["tr1", "tr2", "tr3"], inplace=True)

        # Bandas de Bollinger 
        result["bb_mid"] = result["Close"].rolling(window=window).mean()
        bb_std = result["Close"].rolling(window=window).std()
        result["bb_upper"] = result["bb_mid"] + 2 * bb_std
        result["bb_lower"] = result["bb_mid"] - 2 * bb_std
        result["bb_width"] = (result["bb_upper"] - result["bb_lower"]) / result["bb_mid"]

        # Drawdown máximo 
        rolling_max = result["Close"].cummax()
        result["drawdown"] = (result["Close"] - rolling_max) / rolling_max

        return result

    def analyze(
        self,
        pair: str,
        period: str = "3m",
        window: int = 20,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> "VolatilityReport":
        """
        Método principal: descarga datos y calcula todas las métricas.

        Args:
            pair: Par de divisas
            period: Período de análisis
            window: Ventana para métricas móviles
            start_date: Fecha inicio personalizada
            end_date: Fecha fin personalizada

        Returns:
            VolatilityReport con todos los resultados y métodos de visualización
        """
        print(f" Descargando datos para {pair}...")
        df = self.fetch_data(pair, period, start_date, end_date)
        print(f" {len(df)} registros obtenidos ({df.index[0].date()} → {df.index[-1].date()})")

        print("  Calculando métricas de volatilidad...")
        metrics_df = self.calculate_volatility(df, window=window)

        return VolatilityReport(
            pair=pair,
            period=period,
            window=window,
            data=metrics_df,
        )

    def compare_pairs(
        self,
        pairs: list[str],
        period: str = "3m",
        window: int = 20,
    ) -> pd.DataFrame:
        """
        Compara la volatilidad anualizada de múltiples pares.

        Args:
            pairs: Lista de pares (ej: ['EURUSD', 'GBPUSD', 'USDCOP'])
            period: Período de análisis
            window: Ventana para métricas móviles

        Returns:
            DataFrame resumen con métricas por par
        """
        results = []
        for pair in pairs:
            try:
                report = self.analyze(pair, period, window)
                summary = report.get_summary_dict()
                results.append(summary)
            except Exception as e:
                print(f"  Error en {pair}: {e}")

        if not results:
            raise ValueError("No se pudo obtener datos para ningún par.")

        df = pd.DataFrame(results).set_index("pair")
        return df.sort_values("volatility_annual_pct", ascending=False)


class VolatilityReport:
    """
    Contiene los resultados del análisis de volatilidad para un par de divisas.
    Generado por ForexVolatilityAnalyzer.analyze()
    """

    def __init__(self, pair: str, period: str, window: int, data: pd.DataFrame):
        self.pair = pair.upper()
        self.period = period
        self.window = window
        self.data = data
        self._last = data.dropna().iloc[-1]  # última fila con métricas completas

    def summary(self) -> str:
        #Devuelve un resumen de texto con las métricas principales.
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
            f"  Precio actual     : {d['Close']:.5f}",
            f"  Retorno total     : {total_return:+.2f}%",
            f"  Drawdown máximo   : {max_dd:.2f}%",
            f"{'─' * 55}",
            f"  Volatilidad diaria  (rolling {self.window}d) : {d['volatility_daily']*100:.3f}%",
            f"  Volatilidad anual   (rolling {self.window}d) : {d['volatility_annual']*100:.2f}%",
            f"  ATR ({self.window}d)                         : {d['atr']:.5f}",
            f"{'─' * 55}",
            f"  Banda Bollinger Superior : {d['bb_upper']:.5f}",
            f"  Banda Bollinger Media    : {d['bb_mid']:.5f}",
            f"  Banda Bollinger Inferior : {d['bb_lower']:.5f}",
            f"  Ancho Bandas (BB Width)  : {d['bb_width']*100:.3f}%",
            f"{'═' * 55}\n",
        ]
        return "\n".join(lines)

    def get_summary_dict(self) -> dict:
        #Devuelve métricas como diccionario (útil para comparaciones).
        d = self._last
        return {
            "pair": self.pair,
            "price": round(float(d["Close"]), 5),
            "volatility_daily_pct": round(float(d["volatility_daily"]) * 100, 4),
            "volatility_annual_pct": round(float(d["volatility_annual"]) * 100, 2),
            "atr": round(float(d["atr"]), 5),
            "bb_width_pct": round(float(d["bb_width"]) * 100, 4),
            "cumulative_return_pct": round(float(self.data["cumulative_return"].iloc[-1]) * 100, 2),
            "max_drawdown_pct": round(float(self.data["drawdown"].min()) * 100, 2),
            "n_observations": len(self.data),
        }
