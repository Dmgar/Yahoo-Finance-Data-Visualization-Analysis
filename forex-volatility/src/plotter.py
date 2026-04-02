"""
Módulo de visualización para el análisis de volatilidad de divisas.
Genera gráficos interactivos con matplotlib/seaborn y exportables como PNG.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
from typing import Optional

from volatility_analyzer import VolatilityReport, ForexVolatilityAnalyzer


#  Tema visual
DARK_BG    = "#0d1117"
PANEL_BG   = "#161b22"
GRID_COLOR = "#21262d"
TEXT_COLOR = "#e6edf3"
ACCENT     = "#58a6ff"
GREEN      = "#3fb950"
RED        = "#f85149"
YELLOW     = "#d29922"
PURPLE     = "#a371f7"
ORANGE     = "#db6d28"

def _setup_style():
    plt.rcParams.update({
        "figure.facecolor":  DARK_BG,
        "axes.facecolor":    PANEL_BG,
        "axes.edgecolor":    GRID_COLOR,
        "axes.labelcolor":   TEXT_COLOR,
        "axes.grid":         True,
        "grid.color":        GRID_COLOR,
        "grid.linestyle":    "--",
        "grid.linewidth":    0.5,
        "text.color":        TEXT_COLOR,
        "xtick.color":       TEXT_COLOR,
        "ytick.color":       TEXT_COLOR,
        "legend.facecolor":  PANEL_BG,
        "legend.edgecolor":  GRID_COLOR,
        "font.family":       "monospace",
    })


def plot_full_analysis(
    report: VolatilityReport,
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Genera un dashboard completo de análisis de volatilidad.

    Incluye 5 paneles:
    1. Precio con Bandas de Bollinger
    2. Retornos diarios (log returns)
    3. Volatilidad histórica rolling
    4. ATR (Average True Range)
    5. Drawdown

    Args:
        report: VolatilityReport generado por ForexVolatilityAnalyzer
        save_path: Ruta para guardar la imagen (opcional)
        show: Si mostrar la ventana interactiva

    Returns:
        Figura de matplotlib
    """
    _setup_style()
    df = report.data.dropna()

    fig = plt.figure(figsize=(16, 14), facecolor=DARK_BG)
    fig.suptitle(
        f"Análisis de Volatilidad — {report.pair}   |   "
        f"Período: {df.index[0].strftime('%Y-%m-%d')} → {df.index[-1].strftime('%Y-%m-%d')}",
        color=TEXT_COLOR, fontsize=14, fontweight="bold", y=0.98,
    )

    gs = gridspec.GridSpec(
        5, 1, figure=fig,
        height_ratios=[3, 1.2, 1.2, 1, 1],
        hspace=0.08,
    )

    axes = [fig.add_subplot(gs[i]) for i in range(5)]
    for ax in axes[:-1]:
        ax.tick_params(labelbottom=False)

    #  Panel 1: Precio + Bollinger Bands 
    ax = axes[0]
    ax.plot(df.index, df["Close"], color=ACCENT, linewidth=1.5, label="Precio", zorder=3)
    ax.plot(df.index, df["bb_upper"], color=YELLOW, linewidth=0.8, linestyle="--", label="BB Superior", alpha=0.8)
    ax.plot(df.index, df["bb_mid"],   color=TEXT_COLOR, linewidth=0.8, linestyle="--", label=f"BB Media ({report.window}d)", alpha=0.6)
    ax.plot(df.index, df["bb_lower"], color=YELLOW, linewidth=0.8, linestyle="--", label="BB Inferior", alpha=0.8)
    ax.fill_between(df.index, df["bb_lower"], df["bb_upper"], alpha=0.07, color=YELLOW)
    ax.set_ylabel("Precio", color=TEXT_COLOR, fontsize=10)
    ax.legend(loc="upper left", fontsize=8, ncol=4)
    ax.set_facecolor(PANEL_BG)
    _add_watermark(ax)

    #  Panel 2: Log Returns
    ax = axes[1]
    colors = [GREEN if r >= 0 else RED for r in df["log_return"]]
    ax.bar(df.index, df["log_return"] * 100, color=colors, width=0.8, alpha=0.85)
    ax.axhline(0, color=GRID_COLOR, linewidth=0.8)
    ax.set_ylabel("Retorno (%)", color=TEXT_COLOR, fontsize=9)
    ax.text(0.01, 0.92, "Retornos Logarítmicos Diarios", transform=ax.transAxes,
            color=TEXT_COLOR, fontsize=8, alpha=0.7)

    #  Panel 3: Volatilidad anualizada 
    ax = axes[2]
    vol_pct = df["volatility_annual"] * 100
    ax.plot(df.index, vol_pct, color=PURPLE, linewidth=1.5, label="Vol. Anualizada")
    ax.fill_between(df.index, vol_pct, alpha=0.15, color=PURPLE)
    # Líneas de referencia
    for lvl, lbl in [(5, "Baja"), (10, "Media"), (20, "Alta")]:
        ax.axhline(lvl, color=GRID_COLOR, linewidth=0.7, linestyle=":")
        ax.text(df.index[-1], lvl, f" {lbl}", va="center", color=GRID_COLOR, fontsize=7)
    ax.set_ylabel("Vol. Anual (%)", color=TEXT_COLOR, fontsize=9)
    ax.legend(loc="upper left", fontsize=8)

    # Panel 4: ATR
    ax = axes[3]
    ax.plot(df.index, df["atr"], color=ORANGE, linewidth=1.3, label=f"ATR ({report.window}d)")
    ax.fill_between(df.index, df["atr"], alpha=0.12, color=ORANGE)
    ax.set_ylabel("ATR", color=TEXT_COLOR, fontsize=9)
    ax.legend(loc="upper left", fontsize=8)

    #  Panel 5: Drawdown 
    ax = axes[4]
    ax.fill_between(df.index, df["drawdown"] * 100, 0, color=RED, alpha=0.5)
    ax.plot(df.index, df["drawdown"] * 100, color=RED, linewidth=0.8)
    ax.set_ylabel("Drawdown (%)", color=TEXT_COLOR, fontsize=9)
    ax.set_xlabel("Fecha", color=TEXT_COLOR, fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.97])

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
        print(f" Gráfico guardado en: {save_path}")

    if show:
        plt.show()

    return fig


def plot_comparison(
    comparison_df: pd.DataFrame,
    save_path: Optional[str] = None,
    show: bool = True,
) -> plt.Figure:
    """
    Gráfico comparativo de volatilidad entre múltiples pares.

    Args:
        comparison_df: DataFrame de ForexVolatilityAnalyzer.compare_pairs()
        save_path: Ruta para guardar
        show: Si mostrar la ventana

    Returns:
        Figura de matplotlib
    """
    _setup_style()

    df = comparison_df.copy().reset_index()
    df = df.sort_values("volatility_annual_pct", ascending=True)

    fig, axes = plt.subplots(1, 3, figsize=(16, max(5, len(df) * 0.7 + 2)), facecolor=DARK_BG)
    fig.suptitle("Comparación de Volatilidad entre Pares de Divisas",
                 color=TEXT_COLOR, fontsize=13, fontweight="bold")

    # Paleta por nivel de volatilidad
    def vol_color(v):
        if v < 5:   return GREEN
        elif v < 12: return YELLOW
        else:        return RED

    colors = [vol_color(v) for v in df["volatility_annual_pct"]]

    #  Barras: volatilidad anualizada 
    ax = axes[0]
    bars = ax.barh(df["pair"], df["volatility_annual_pct"], color=colors, edgecolor=PANEL_BG, linewidth=0.5)
    ax.set_xlabel("Volatilidad Anualizada (%)", color=TEXT_COLOR, fontsize=9)
    ax.set_title("Volatilidad Anualizada", color=TEXT_COLOR, fontsize=10)
    for bar, val in zip(bars, df["volatility_annual_pct"]):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", ha="left", fontsize=8, color=TEXT_COLOR)

    #  Barras: retorno acumulado 
    ax = axes[1]
    ret_colors = [GREEN if v >= 0 else RED for v in df["cumulative_return_pct"]]
    bars2 = ax.barh(df["pair"], df["cumulative_return_pct"], color=ret_colors, edgecolor=PANEL_BG, linewidth=0.5)
    ax.axvline(0, color=TEXT_COLOR, linewidth=0.8, alpha=0.5)
    ax.set_xlabel("Retorno Acumulado (%)", color=TEXT_COLOR, fontsize=9)
    ax.set_title("Retorno Acumulado", color=TEXT_COLOR, fontsize=10)
    for bar, val in zip(bars2, df["cumulative_return_pct"]):
        xpos = val + 0.05 if val >= 0 else val - 0.05
        ha = "left" if val >= 0 else "right"
        ax.text(xpos, bar.get_y() + bar.get_height() / 2,
                f"{val:+.1f}%", va="center", ha=ha, fontsize=8, color=TEXT_COLOR)

    #  Scatter: riesgo vs retorno 
    ax = axes[2]
    sc = ax.scatter(
        df["volatility_annual_pct"],
        df["cumulative_return_pct"],
        c=[vol_color(v) for v in df["volatility_annual_pct"]],
        s=120, edgecolors=TEXT_COLOR, linewidths=0.5, zorder=3,
    )
    ax.axhline(0, color=GRID_COLOR, linewidth=0.8, linestyle="--")
    for _, row in df.iterrows():
        ax.annotate(row["pair"],
                    (row["volatility_annual_pct"], row["cumulative_return_pct"]),
                    textcoords="offset points", xytext=(6, 3),
                    fontsize=7, color=TEXT_COLOR)
    ax.set_xlabel("Volatilidad Anualizada (%)", color=TEXT_COLOR, fontsize=9)
    ax.set_ylabel("Retorno Acumulado (%)", color=TEXT_COLOR, fontsize=9)
    ax.set_title("Riesgo vs. Retorno", color=TEXT_COLOR, fontsize=10)

    for ax in axes:
        ax.set_facecolor(PANEL_BG)
        ax.tick_params(colors=TEXT_COLOR, labelsize=8)
        ax.spines[:].set_color(GRID_COLOR)

    plt.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
        print(f" Comparación guardada en: {save_path}")

    if show:
        plt.show()

    return fig


def _add_watermark(ax):
    ax.text(0.99, 0.02, "forex-volatility | Yahoo Finance",
            transform=ax.transAxes, color=GRID_COLOR,
            fontsize=7, ha="right", va="bottom", alpha=0.6)
