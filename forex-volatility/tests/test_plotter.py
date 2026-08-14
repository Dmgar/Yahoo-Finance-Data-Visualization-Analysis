"""Tests unitarios para src/plotter.py (backend Agg, sin ventanas)."""

import matplotlib.pyplot as plt
import pytest

import plotter
from plotter import _add_watermark, _setup_style, plot_comparison, plot_full_analysis
from theme import DARK_BG, FONT_FAMILY, GRID_COLOR, PANEL_BG


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


class TestSetupStyle:
    def test_applies_dark_theme_rcparams(self):
        _setup_style()

        assert plt.rcParams["figure.facecolor"] == DARK_BG
        assert plt.rcParams["axes.facecolor"] == PANEL_BG
        assert plt.rcParams["grid.color"] == GRID_COLOR
        assert plt.rcParams["axes.grid"] is True
        assert FONT_FAMILY in plt.rcParams["font.family"]


class TestPlotFullAnalysis:
    def test_returns_figure_with_five_panels(self, offline_report):
        fig = plot_full_analysis(offline_report, show=False)

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 5

    def test_title_includes_pair_and_date_range(self, offline_report):
        fig = plot_full_analysis(offline_report, show=False)
        title = fig._suptitle.get_text()

        assert offline_report.pair in title
        assert offline_report.data.index[0].strftime("%Y-%m-%d") in title
        assert offline_report.data.index[-1].strftime("%Y-%m-%d") in title

    def test_only_last_panel_shows_xtick_labels(self, offline_report):
        fig = plot_full_analysis(offline_report, show=False)

        assert all(not label.get_visible() for ax in fig.axes[:-1] for label in ax.get_xticklabels())

    def test_panels_have_expected_ylabels(self, offline_report):
        fig = plot_full_analysis(offline_report, show=False)

        assert [ax.get_ylabel() for ax in fig.axes] == [
            "Precio",
            "Retorno (%)",
            "Vol. Anual (%)",
            "ATR",
            "Drawdown (%)",
        ]

    def test_works_without_technical_indicators(self, offline_report_no_indicators):
        fig = plot_full_analysis(offline_report_no_indicators, show=False)

        assert len(fig.axes) == 5

    def test_save_path_creates_file_and_parent_dir(self, offline_report, tmp_path, capsys):
        save_path = tmp_path / "nested" / "eurusd.png"
        plot_full_analysis(offline_report, save_path=str(save_path), show=False)

        assert save_path.exists()
        assert save_path.stat().st_size > 0
        assert str(save_path) in capsys.readouterr().out

    def test_show_true_calls_pyplot_show(self, offline_report, monkeypatch):
        calls = []
        monkeypatch.setattr(plotter.plt, "show", lambda *a, **k: calls.append(1))
        plot_full_analysis(offline_report, show=True)

        assert calls == [1]

    def test_no_file_written_without_save_path(self, offline_report, tmp_path):
        plot_full_analysis(offline_report, show=False)

        assert list(tmp_path.iterdir()) == []


class TestPlotComparison:
    def test_returns_figure_with_three_panels(self, comparison_df):
        fig = plot_comparison(comparison_df, show=False)

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 3
        assert [ax.get_title() for ax in fig.axes] == [
            "Volatilidad Anualizada",
            "Retorno Acumulado",
            "Riesgo vs. Retorno",
        ]

    def test_bars_sorted_ascending_by_volatility(self, comparison_df):
        fig = plot_comparison(comparison_df, show=False)
        labels = [label.get_text() for label in fig.axes[0].get_yticklabels()]

        assert labels == ["EURUSD", "GBPUSD", "USDARS"]

    def test_bar_widths_match_volatility_values(self, comparison_df):
        fig = plot_comparison(comparison_df, show=False)
        widths = [patch.get_width() for patch in fig.axes[0].patches]

        assert widths == pytest.approx([4.1, 8.4, 23.8])

    def test_input_dataframe_is_not_mutated(self, comparison_df):
        before = comparison_df.copy()
        plot_comparison(comparison_df, show=False)

        assert comparison_df.equals(before)

    def test_single_pair_is_supported(self, comparison_df):
        fig = plot_comparison(comparison_df.head(1), show=False)

        assert len(fig.axes[0].patches) == 1

    def test_save_path_writes_png(self, comparison_df, tmp_path, capsys):
        save_path = tmp_path / "out" / "comparison.png"
        plot_comparison(comparison_df, save_path=str(save_path), show=False)

        assert save_path.exists()
        assert "Comparación guardada" in capsys.readouterr().out

    def test_show_true_calls_pyplot_show(self, comparison_df, monkeypatch):
        calls = []
        monkeypatch.setattr(plotter.plt, "show", lambda *a, **k: calls.append(1))
        plot_comparison(comparison_df, show=True)

        assert calls == [1]


class TestAddWatermark:
    def test_adds_watermark_text(self):
        _, ax = plt.subplots()
        _add_watermark(ax)

        assert [t.get_text() for t in ax.texts] == ["forex-volatility | Yahoo Finance"]
