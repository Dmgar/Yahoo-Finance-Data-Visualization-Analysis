"""
Tests unitarios para el módulo de análisis de volatilidad.

Ejecutar con:
    pytest tests/ -v
    pytest tests/ -v --tb=short
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import pandas as pd
import numpy as np

from volatility_analyzer import ForexVolatilityAnalyzer, VolatilityReport, FOREX_PAIRS, PERIODS


#  Fixtures 

@pytest.fixture(scope="module")
def analyzer():
    return ForexVolatilityAnalyzer()


@pytest.fixture(scope="module")
def sample_report(analyzer):
    """Descarga datos reales una sola vez para todos los tests."""
    return analyzer.analyze("EURUSD", period="1m", window=10)


@pytest.fixture
def mock_df():
    """DataFrame simulado sin conexión a internet."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=100, freq="B")
    close = 1.08 + np.cumsum(np.random.normal(0, 0.005, 100))
    high  = close + np.abs(np.random.normal(0, 0.003, 100))
    low   = close - np.abs(np.random.normal(0, 0.003, 100))
    return pd.DataFrame({"Open": close, "High": high, "Low": low, "Close": close, "Volume": 0}, index=dates)


#  Tests: ForexVolatilityAnalyzer 

class TestForexVolatilityAnalyzer:

    def test_get_ticker_format(self, analyzer):
        assert analyzer._get_ticker("EURUSD")   == "EURUSD=X"
        assert analyzer._get_ticker("EUR/USD")  == "EURUSD=X"
        assert analyzer._get_ticker("eur-usd")  == "EURUSD=X"

    def test_invalid_period_raises(self, analyzer):
        with pytest.raises(ValueError, match="no válido"):
            analyzer.fetch_data("EURUSD", period="5d")

    def test_fetch_data_returns_dataframe(self, analyzer):
        df = analyzer.fetch_data("EURUSD", period="1m")
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "Close" in df.columns
        assert "High"  in df.columns
        assert "Low"   in df.columns

    def test_fetch_data_no_nulls(self, analyzer):
        df = analyzer.fetch_data("EURUSD", period="1m")
        assert df["Close"].isna().sum() == 0

    def test_calculate_volatility_columns(self, analyzer, mock_df):
        result = analyzer.calculate_volatility(mock_df, window=10)
        expected_cols = [
            "log_return", "volatility_daily", "volatility_annual",
            "cumulative_return", "true_range", "atr",
            "bb_mid", "bb_upper", "bb_lower", "bb_width", "drawdown",
        ]
        for col in expected_cols:
            assert col in result.columns, f"Falta columna: {col}"

    def test_volatility_is_positive(self, analyzer, mock_df):
        result = analyzer.calculate_volatility(mock_df, window=10).dropna()
        assert (result["volatility_daily"] >= 0).all()
        assert (result["volatility_annual"] >= 0).all()
        assert (result["atr"] >= 0).all()

    def test_bollinger_bands_order(self, analyzer, mock_df):
        result = analyzer.calculate_volatility(mock_df, window=10).dropna()
        assert (result["bb_upper"] >= result["bb_mid"]).all()
        assert (result["bb_mid"]   >= result["bb_lower"]).all()

    def test_drawdown_is_non_positive(self, analyzer, mock_df):
        result = analyzer.calculate_volatility(mock_df, window=10).dropna()
        assert (result["drawdown"] <= 0).all()

    def test_annualization_factor(self):
        a = ForexVolatilityAnalyzer(annualization_factor=365)
        assert a.annualization_factor == 365


#  Tests: VolatilityReport 

class TestVolatilityReport:

    def test_summary_is_string(self, sample_report):
        s = sample_report.summary()
        assert isinstance(s, str)
        assert "EURUSD" in s

    def test_summary_contains_key_metrics(self, sample_report):
        s = sample_report.summary()
        for keyword in ["Precio", "Volatilidad", "ATR", "Bollinger", "Drawdown"]:
            assert keyword in s, f"Falta keyword en summary: {keyword}"

    def test_get_summary_dict_keys(self, sample_report):
        d = sample_report.get_summary_dict()
        expected_keys = [
            "pair", "price", "volatility_daily_pct", "volatility_annual_pct",
            "atr", "bb_width_pct", "cumulative_return_pct", "max_drawdown_pct", "n_observations",
        ]
        for key in expected_keys:
            assert key in d, f"Falta key en dict: {key}"

    def test_get_summary_dict_types(self, sample_report):
        d = sample_report.get_summary_dict()
        assert isinstance(d["pair"], str)
        assert isinstance(d["price"], float)
        assert isinstance(d["volatility_annual_pct"], float)
        assert isinstance(d["n_observations"], int)

    def test_pair_is_uppercase(self, sample_report):
        assert sample_report.pair == sample_report.pair.upper()


#  Tests: constantes 

class TestConstants:

    def test_forex_pairs_not_empty(self):
        assert len(FOREX_PAIRS) > 0

    def test_periods_have_days_and_label(self):
        for key, val in PERIODS.items():
            assert "days"  in val, f"Período '{key}' sin 'days'"
            assert "label" in val, f"Período '{key}' sin 'label'"
            assert val["days"] > 0


#  Tests: comparación de pares 

class TestComparePairs:

    def test_compare_returns_dataframe(self, analyzer):
        result = analyzer.compare_pairs(["EURUSD", "GBPUSD"], period="1m")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_compare_sorted_by_volatility(self, analyzer):
        result = analyzer.compare_pairs(["EURUSD", "GBPUSD", "USDJPY"], period="1m")
        vols = result["volatility_annual_pct"].tolist()
        assert vols == sorted(vols, reverse=True)
