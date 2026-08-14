import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional
from volatility_analyzer import VolatilityReport
from theme import DARK_BG, TEXT_COLOR, ACCENT, GREEN, RED, YELLOW, PURPLE, ORANGE


def plot_interactive_analysis(
    report: VolatilityReport,
    save_path: Optional[str] = None,
    show: bool = True,
) -> go.Figure:
    """
    Genera un dashboard interactivo completo usando Plotly.
    """
    df = report.data
    
    # Crear subplots: 4 filas, 1 columna
    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            f"Precio y Tendencias - {report.pair}",
            "RSI (14d)",
            "MACD",
            "Volatilidad Anual (%)",
        ),
        row_heights=[0.5, 0.15, 0.15, 0.2],
    )

    # --- 1. Precio + SMA ---
    # Usamos una copia limpia para el precio para evitar problemas de renderizado
    df_price = df.dropna(subset=["Close"])
    fig.add_trace(
        go.Candlestick(
            x=df_price.index,
            open=df_price["Open"],
            high=df_price["High"],
            low=df_price["Low"],
            close=df_price["Close"],
            name="Precio",
            increasing_line_color=GREEN,
            decreasing_line_color=RED,
        ),
        row=1,
        col=1,
    )

    for window in [20, 50, 200]:
        col = f"sma_{window}"
        if col in df.columns:
            df_sma = df.dropna(subset=[col])
            fig.add_trace(
                go.Scatter(
                    x=df_sma.index, y=df_sma[col], name=f"SMA {window}", line=dict(width=1.5)
                ),
                row=1,
                col=1,
            )

    # --- 2. RSI ---
    if "rsi" in df.columns:
        df_rsi = df.dropna(subset=["rsi"])
        if not df_rsi.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_rsi.index, y=df_rsi["rsi"], name="RSI", line=dict(color=PURPLE, width=1.5)
                ),
                row=2,
                col=1,
            )
            fig.add_hline(y=70, line_dash="dash", line_color=RED, row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color=GREEN, row=2, col=1)
            fig.update_yaxes(range=[0, 100], row=2, col=1)

    # --- 3. MACD ---
    if "macd" in df.columns:
        df_macd = df.dropna(subset=["macd", "macd_signal", "macd_hist"])
        if not df_macd.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_macd.index, y=df_macd["macd"], name="MACD", line=dict(color=ACCENT, width=1.5)
                ),
                row=3,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=df_macd.index, y=df_macd["macd_signal"], name="Signal", line=dict(color=ORANGE, width=1.2)
                ),
                row=3,
                col=1,
            )
            fig.add_trace(
                go.Bar(
                    x=df_macd.index,
                    y=df_macd["macd_hist"],
                    name="Histogram",
                    marker_color=[GREEN if v >= 0 else RED for v in df_macd["macd_hist"]],
                ),
                row=3,
                col=1,
            )

    # --- 4. Volatilidad ---
    df_vol = df.dropna(subset=["volatility_annual"])
    if not df_vol.empty:
        fig.add_trace(
            go.Scatter(
                x=df_vol.index,
                y=df_vol["volatility_annual"] * 100,
                name="Vol. Anual %",
                line=dict(color=YELLOW, width=1.5),
                fill="tozeroy",
            ),
            row=4,
            col=1,
        )


    # --- Configuración Global de Estilo ---
    fig.update_layout(
        title=f"Análisis de Volatilidad y Tendencias — {report.pair}",
        template="plotly_dark",
        xaxis4_title="Fecha",
        yaxis_title="Precio",
        height=1000,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        margin=dict(l=50, r=50, t=80, b=50),
    )

    # Mejorar el eje X con un range slider solo en el gráfico de precio
    fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
    fig.update_xaxes(rangeslider_visible=True, row=4, col=1)

    if save_path:
        fig.write_html(save_path)
        print(f" Dashboard interactivo guardado en: {save_path}")

    if show:
        fig.show()

    return fig
