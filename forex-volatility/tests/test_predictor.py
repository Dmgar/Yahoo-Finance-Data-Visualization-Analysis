"""Tests unitarios para src/predictor.py (sin conexión a internet)."""

import numpy as np
import pandas as pd
import pytest

from predictor import ForexPredictor
from volatility_analyzer import VolatilityReport


def build_report(close, atr=None, pair="EURUSD") -> VolatilityReport:
    index = pd.date_range("2024-01-01", periods=len(close), freq="B")
    data = {"Close": np.asarray(close, dtype=float)}
    if atr is not None:
        data["atr"] = np.asarray(atr, dtype=float)
    return VolatilityReport(
        pair=pair, period="3m", window=20, data=pd.DataFrame(data, index=index)
    )


class TestPredictTrend:
    def test_upward_series_is_alcista(self):
        report = build_report(np.linspace(1.0, 1.2, 40))
        result = ForexPredictor(projection_days=5).predict_trend(report)

        assert result["trend"] == "Alcista"
        assert result["projected_price"] > result["current_price"]
        assert result["pct_change"] > 0
        assert result["days"] == 5

    def test_downward_series_is_bajista(self):
        report = build_report(np.linspace(1.2, 1.0, 40))
        result = ForexPredictor().predict_trend(report)

        assert result["trend"] == "Bajista"
        assert result["projected_price"] < result["current_price"]
        assert result["pct_change"] < 0

    def test_uses_only_last_30_observations(self):
        """Un tramo antiguo con tendencia opuesta no debe alterar la proyección."""
        close = np.concatenate([np.linspace(2.0, 1.0, 50), np.linspace(1.0, 1.5, 30)])
        result = ForexPredictor().predict_trend(build_report(close))

        assert result["trend"] == "Alcista"

    def test_projection_days_extends_horizon(self):
        report = build_report(np.linspace(1.0, 1.2, 40))
        short = ForexPredictor(projection_days=1).predict_trend(report)
        long = ForexPredictor(projection_days=10).predict_trend(report)

        assert long["projected_price"] > short["projected_price"]
        assert long["days"] == 10

    def test_linear_series_projection_is_exact(self):
        """Con una recta perfecta, la regresión debe extrapolar el siguiente paso."""
        close = np.arange(1.0, 1.3, 0.01)
        result = ForexPredictor(projection_days=1).predict_trend(build_report(close))

        assert result["projected_price"] == pytest.approx(close[-1] + 0.01, abs=1e-6)

    def test_current_price_is_last_close(self):
        close = np.linspace(1.0, 1.2, 40)
        result = ForexPredictor().predict_trend(build_report(close))

        assert result["current_price"] == pytest.approx(close[-1])

    @pytest.mark.parametrize("n_valid", [0, 1])
    def test_insufficient_data_returns_placeholder(self, n_valid):
        close = [np.nan] * 5
        for i in range(n_valid):
            close[i] = 1.1
        result = ForexPredictor(projection_days=3).predict_trend(build_report(close))

        assert result == {
            "trend": "Insuficientes datos",
            "pct_change": 0,
            "projected_price": None,
            "days": 3,
        }

    def test_ignores_nan_rows_from_other_indicators(self):
        """Los NaN de 'atr' no deben vaciar el DataFrame de precios."""
        close = np.linspace(1.0, 1.2, 40)
        atr = [np.nan] * 40
        result = ForexPredictor().predict_trend(build_report(close, atr=atr))

        assert result["trend"] == "Alcista"


class TestPredictVolatilityRange:
    def test_range_is_price_plus_minus_atr(self):
        report = build_report([1.10, 1.20], atr=[0.01, 0.02])
        result = ForexPredictor().predict_volatility_range(report)

        assert result["current_price"] == pytest.approx(1.20)
        assert result["atr"] == pytest.approx(0.02)
        assert result["expected_lower"] == pytest.approx(1.18)
        assert result["expected_upper"] == pytest.approx(1.22)
        assert result["range_pct"] == pytest.approx(0.02 / 1.20 * 100)

    def test_uses_last_row_with_both_values(self):
        report = build_report([1.10, 1.20, 1.30], atr=[0.01, 0.02, np.nan])
        result = ForexPredictor().predict_volatility_range(report)

        assert result["current_price"] == pytest.approx(1.20)
        assert result["atr"] == pytest.approx(0.02)

    def test_all_nan_atr_returns_empty_payload(self):
        report = build_report([1.10, 1.20], atr=[np.nan, np.nan])
        result = ForexPredictor().predict_volatility_range(report)

        assert result == {
            "current_price": None,
            "atr": None,
            "expected_lower": None,
            "expected_upper": None,
            "range_pct": None,
        }


class TestGetFullProjection:
    def test_combines_trend_and_volatility(self, offline_report):
        result = ForexPredictor().get_full_projection(offline_report)

        assert set(result) == {"trend", "volatility"}
        assert result["trend"]["trend"] in {"Alcista", "Bajista"}
        assert result["volatility"]["expected_upper"] > result["volatility"]["expected_lower"]

    def test_matches_individual_calls(self, offline_report):
        predictor = ForexPredictor()
        full = predictor.get_full_projection(offline_report)

        assert full["trend"] == predictor.predict_trend(offline_report)
        assert full["volatility"] == predictor.predict_volatility_range(offline_report)
