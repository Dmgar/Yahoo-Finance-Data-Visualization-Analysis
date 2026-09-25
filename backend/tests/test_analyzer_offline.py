"""Tests de volatility_analyzer que sustituyen la descarga de Yahoo Finance.

Complementan test_analyzer.py cubriendo rutas de error y de configuración que
requerirían red o datos incompletos.
"""

import logging

import numpy as np
import pandas as pd
import pytest
from conftest import make_ohlc

import volatility_analyzer
from volatility_analyzer import (
    ForexDataError,
    ForexVolatilityAnalyzer,
    VolatilityReport,
)


@pytest.fixture
def fake_download(monkeypatch):
    """Sustituye yf.download y registra los argumentos recibidos."""
    calls = []

    def _install(df):
        def _download(ticker, **kwargs):
            calls.append({"ticker": ticker, **kwargs})
            return df

        monkeypatch.setattr(volatility_analyzer.yf, "download", _download)
        return calls

    return _install


class TestFetchData:
    def test_uses_explicit_date_range(self, offline_analyzer, fake_download):
        calls = fake_download(make_ohlc(periods=30))
        offline_analyzer.fetch_data(
            "eur/usd", start_date="2024-01-01", end_date="2024-02-01"
        )

        assert calls == [
            {
                "ticker": "EURUSD=X",
                "start": "2024-01-01",
                "end": "2024-02-01",
                "progress": False,
            }
        ]

    def test_period_is_translated_to_day_window(self, offline_analyzer, fake_download):
        calls = fake_download(make_ohlc(periods=30))
        offline_analyzer.fetch_data("EURUSD", period="1w")
        span = calls[0]["end"] - calls[0]["start"]

        assert span.days == volatility_analyzer.PERIODS["1w"]["days"]

    def test_empty_response_raises(self, offline_analyzer, fake_download):
        fake_download(pd.DataFrame())
        with pytest.raises(ForexDataError, match="No se obtuvieron datos"):
            offline_analyzer.fetch_data("EURUSD", period="1m")

    @pytest.mark.parametrize(
        "dates", [{"start_date": "2024-01-01"}, {"end_date": "2024-02-01"}]
    )
    def test_incomplete_date_range_raises_instead_of_falling_back(
        self, offline_analyzer, fake_download, dates
    ):
        calls = fake_download(make_ohlc(periods=30))
        with pytest.raises(ValueError, match="juntos"):
            offline_analyzer.fetch_data("EURUSD", **dates)

        assert calls == []

    def test_download_failure_is_wrapped_with_cause(self, offline_analyzer, monkeypatch):
        original = ConnectionError("host inalcanzable")

        def _download(ticker, **kwargs):
            raise original

        monkeypatch.setattr(volatility_analyzer.yf, "download", _download)
        with pytest.raises(ForexDataError, match="EURUSD=X") as exc:
            offline_analyzer.fetch_data("EURUSD", period="1m")

        assert exc.value.__cause__ is original

    def test_missing_ohlc_column_raises(self, offline_analyzer, fake_download):
        fake_download(make_ohlc(periods=30).drop(columns=["High"]))
        with pytest.raises(ForexDataError, match=r"\['High'\]"):
            offline_analyzer.fetch_data("EURUSD", period="1m")

    def test_all_null_rows_raise(self, offline_analyzer, fake_download):
        df = make_ohlc(periods=30)
        df["Close"] = np.nan
        fake_download(df)
        with pytest.raises(ForexDataError, match="valores nulos"):
            offline_analyzer.fetch_data("EURUSD", period="1m")

    def test_flattens_multiindex_columns(self, offline_analyzer, fake_download):
        df = make_ohlc(periods=30)
        df.columns = pd.MultiIndex.from_product([df.columns, ["EURUSD=X"]])
        fake_download(df)
        result = offline_analyzer.fetch_data("EURUSD", period="1m")

        assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]

    def test_drops_rows_with_nulls(self, offline_analyzer, fake_download):
        df = make_ohlc(periods=30)
        df.iloc[3, df.columns.get_loc("Close")] = np.nan
        fake_download(df)
        result = offline_analyzer.fetch_data("EURUSD", period="1m")

        assert len(result) == 29
        assert isinstance(result.index, pd.DatetimeIndex)


class TestAnalyze:
    def test_indicators_are_added_only_when_requested(self, offline_analyzer, fake_download):
        fake_download(make_ohlc(periods=60))
        without = offline_analyzer.analyze("EURUSD", period="3m", window=10)
        with_indicators = offline_analyzer.analyze(
            "EURUSD", period="3m", window=10, include_indicators=True
        )

        assert "rsi" not in without.data.columns
        assert {"rsi", "macd", "sma_20"} <= set(with_indicators.data.columns)

    def test_report_carries_request_metadata(self, offline_analyzer, fake_download):
        fake_download(make_ohlc(periods=60))
        report = offline_analyzer.analyze("eurusd", period="6m", window=15)

        assert (report.pair, report.period, report.window) == ("EURUSD", "6m", 15)


class TestComparePairsOffline:
    def test_skips_pairs_that_fail(self, offline_analyzer, monkeypatch, offline_report):
        def _analyze(pair, *args, **kwargs):
            if pair == "GBPUSD":
                raise ValueError("sin datos")
            return offline_report

        monkeypatch.setattr(offline_analyzer, "analyze", _analyze)
        result = offline_analyzer.compare_pairs(["EURUSD", "GBPUSD"], period="1m")

        assert list(result.index) == ["EURUSD"]

    def test_warns_about_skipped_pairs(
        self, offline_analyzer, monkeypatch, offline_report, caplog
    ):
        def _analyze(pair, *args, **kwargs):
            if pair == "GBPUSD":
                raise ValueError("sin datos")
            return offline_report

        monkeypatch.setattr(offline_analyzer, "analyze", _analyze)
        with caplog.at_level(logging.WARNING):
            offline_analyzer.compare_pairs(["EURUSD", "GBPUSD"], period="1m")

        assert "GBPUSD" in caplog.text

    def test_raises_when_every_pair_fails(self, offline_analyzer, monkeypatch):
        original = ValueError("sin datos")

        def _analyze(pair, *args, **kwargs):
            raise original

        monkeypatch.setattr(offline_analyzer, "analyze", _analyze)
        with pytest.raises(ForexDataError, match="ningún par") as exc:
            offline_analyzer.compare_pairs(["EURUSD", "GBPUSD"], period="1m")

        assert "GBPUSD: sin datos" in str(exc.value)
        assert exc.value.__cause__ is original


class TestReportValidation:
    def test_empty_data_raises(self):
        with pytest.raises(ForexDataError, match="No hay datos"):
            VolatilityReport(
                pair="EURUSD", period="1m", window=20, data=pd.DataFrame()
            )


class TestReportFormatting:
    @pytest.fixture
    def nan_report(self):
        """Reporte con ventana mayor que el histórico: métricas rolling en NaN."""
        analyzer = ForexVolatilityAnalyzer()
        data = analyzer.calculate_volatility(make_ohlc(periods=5), window=20)
        return VolatilityReport(pair="EURUSD", period="1w", window=20, data=data)

    def test_fmt_returns_na_for_nan(self, nan_report):
        assert nan_report._fmt(np.nan) == "N/A"

    def test_fmt_falls_back_to_str_for_non_numeric(self, nan_report):
        assert nan_report._fmt("sin dato") == "sin dato"

    def test_summary_shows_na_instead_of_failing(self, nan_report):
        assert "N/A" in nan_report.summary()

    def test_summary_dict_uses_none_for_nan_metrics(self, nan_report):
        d = nan_report.get_summary_dict()

        assert d["volatility_daily_pct"] is None
        assert d["atr"] is None
        assert d["n_observations"] == 5
