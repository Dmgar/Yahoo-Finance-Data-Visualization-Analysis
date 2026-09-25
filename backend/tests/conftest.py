"""Fixtures compartidas para los tests (sin conexión a internet)."""

import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

matplotlib.use("Agg")

from volatility_analyzer import ForexVolatilityAnalyzer, VolatilityReport


def make_ohlc(periods: int = 260, seed: int = 7) -> pd.DataFrame:
    """Genera un OHLC sintético reproducible."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-02", periods=periods, freq="B")
    close = 1.08 + np.cumsum(rng.normal(0, 0.004, periods))
    high = close + np.abs(rng.normal(0, 0.003, periods))
    low = close - np.abs(rng.normal(0, 0.003, periods))
    return pd.DataFrame(
        {"Open": close, "High": high, "Low": low, "Close": close, "Volume": 0},
        index=dates,
    )


@pytest.fixture
def offline_analyzer():
    return ForexVolatilityAnalyzer()


@pytest.fixture
def offline_report(offline_analyzer):
    """Reporte con métricas de volatilidad e indicadores técnicos, sin red."""
    metrics = offline_analyzer.calculate_volatility(make_ohlc(), window=20)
    metrics = offline_analyzer.calculate_technical_indicators(metrics)
    return VolatilityReport(pair="EURUSD", period="1y", window=20, data=metrics)


@pytest.fixture
def offline_report_no_indicators(offline_analyzer):
    """Reporte sin indicadores técnicos (RSI/MACD/SMA ausentes)."""
    metrics = offline_analyzer.calculate_volatility(make_ohlc(periods=60), window=20)
    return VolatilityReport(pair="USDCOP", period="3m", window=20, data=metrics)


@pytest.fixture
def comparison_df():
    """Salida simulada de ForexVolatilityAnalyzer.compare_pairs()."""
    return pd.DataFrame(
        [
            {
                "pair": "USDARS",
                "price": 950.0,
                "volatility_daily_pct": 1.5,
                "volatility_annual_pct": 23.8,
                "atr": 12.5,
                "bb_width_pct": 5.0,
                "cumulative_return_pct": 14.2,
                "max_drawdown_pct": -3.1,
                "n_observations": 60,
            },
            {
                "pair": "GBPUSD",
                "price": 1.27,
                "volatility_daily_pct": 0.5,
                "volatility_annual_pct": 8.4,
                "atr": 0.008,
                "bb_width_pct": 2.1,
                "cumulative_return_pct": -1.3,
                "max_drawdown_pct": -4.7,
                "n_observations": 60,
            },
            {
                "pair": "EURUSD",
                "price": 1.09,
                "volatility_daily_pct": 0.25,
                "volatility_annual_pct": 4.1,
                "atr": 0.004,
                "bb_width_pct": 1.2,
                "cumulative_return_pct": 0.8,
                "max_drawdown_pct": -1.9,
                "n_observations": 60,
            },
        ]
    ).set_index("pair")
