"""Tests unitarios para src/interactive_plotter.py."""

import plotly.graph_objects as go

from interactive_plotter import plot_interactive_analysis
from theme import DARK_BG, GREEN, RED


def trace_names(fig) -> list[str]:
    return [trace.name for trace in fig.data]


class TestPlotInteractiveAnalysis:
    def test_returns_figure_with_expected_traces(self, offline_report):
        fig = plot_interactive_analysis(offline_report, show=False)

        assert isinstance(fig, go.Figure)
        assert trace_names(fig) == [
            "Precio",
            "SMA 20",
            "SMA 50",
            "SMA 200",
            "RSI",
            "MACD",
            "Signal",
            "Histogram",
            "Vol. Anual %",
        ]

    def test_candlestick_uses_theme_colors(self, offline_report):
        fig = plot_interactive_analysis(offline_report, show=False)
        candles = fig.data[0]

        assert isinstance(candles, go.Candlestick)
        assert candles.increasing.line.color == GREEN
        assert candles.decreasing.line.color == RED

    def test_layout_uses_dark_theme(self, offline_report):
        fig = plot_interactive_analysis(offline_report, show=False)

        assert offline_report.pair in fig.layout.title.text
        assert fig.layout.template.layout.paper_bgcolor is not None
        assert fig.layout.paper_bgcolor == DARK_BG
        assert fig.layout.plot_bgcolor == DARK_BG
        assert fig.layout.height == 1000

    def test_rsi_panel_is_bounded_and_has_thresholds(self, offline_report):
        fig = plot_interactive_analysis(offline_report, show=False)

        assert tuple(fig.layout.yaxis2.range) == (0, 100)
        assert sorted(shape.y0 for shape in fig.layout.shapes) == [30, 70]

    def test_macd_histogram_colors_follow_sign(self, offline_report):
        fig = plot_interactive_analysis(offline_report, show=False)
        histogram = next(t for t in fig.data if t.name == "Histogram")
        expected = [GREEN if v >= 0 else RED for v in histogram.y]

        assert list(histogram.marker.color) == expected

    def test_rangeslider_only_on_bottom_panel(self, offline_report):
        fig = plot_interactive_analysis(offline_report, show=False)

        assert fig.layout.xaxis.rangeslider.visible is False
        assert fig.layout.xaxis4.rangeslider.visible is True

    def test_skips_indicator_panels_when_columns_missing(
        self, offline_report_no_indicators
    ):
        fig = plot_interactive_analysis(offline_report_no_indicators, show=False)

        assert trace_names(fig) == ["Precio", "Vol. Anual %"]
        assert fig.layout.shapes == ()

    def test_volatility_trace_is_scaled_to_percent(self, offline_report):
        fig = plot_interactive_analysis(offline_report, show=False)
        vol_trace = next(t for t in fig.data if t.name == "Vol. Anual %")
        expected = offline_report.data["volatility_annual"].dropna() * 100

        assert list(vol_trace.y) == list(expected)

    def test_save_path_writes_html(self, offline_report, tmp_path, capsys):
        save_path = tmp_path / "dashboard.html"
        plot_interactive_analysis(offline_report, save_path=str(save_path), show=False)

        assert "<html>" in save_path.read_text()
        assert str(save_path) in capsys.readouterr().out

    def test_show_true_calls_figure_show(self, offline_report, monkeypatch):
        calls = []
        monkeypatch.setattr(go.Figure, "show", lambda self, *a, **k: calls.append(1))
        plot_interactive_analysis(offline_report, show=True)

        assert calls == [1]
