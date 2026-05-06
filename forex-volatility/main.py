# Punto de entrada CLI para el análisis de volatilidad de divisas.
"""
Uso:
    python main.py                              # Análisis interactivo
    python main.py --pair EURUSD --period 3m    # Análisis directo
    python main.py --compare --period 6m        # Comparar todos los pares
    python main.py --pair USDCOP --save         # Guardar gráfico
"""

import argparse
import sys
import logging
from pathlib import Path

# Asegurar que src/ esté en el path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from volatility_analyzer import ForexVolatilityAnalyzer, FOREX_PAIRS, PERIODS
from plotter import plot_full_analysis, plot_comparison
from interactive_plotter import plot_interactive_analysis
from predictor import ForexPredictor


def parse_args():
    parser = argparse.ArgumentParser(
        description=" Análisis de Volatilidad de Divisas — Yahoo Finance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --pair EURUSD --format png
  python main.py --pair USDCOP --format html --indicators
  python main.py --pair GBPUSD --format both --predict --save
  python main.py --compare --period 6m
        """,
    )
    parser.add_argument("--pair", type=str, help="Par de divisas (ej: EURUSD, USDCOP)")
    parser.add_argument(
        "--period",
        type=str,
        default="3m",
        choices=list(PERIODS.keys()),
        help="Período de análisis",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=20,
        help="Ventana para métricas rolling (default: 20)",
    )
    parser.add_argument("--start", type=str, help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument(
        "--compare", action="store_true", help="Comparar múltiples pares"
    )
    parser.add_argument(
        "--pairs", type=str, nargs="+", help="Pares para comparar (con --compare)"
    )
    parser.add_argument(
        "--save", action="store_true", help="Guardar gráficos en /data/"
    )
    parser.add_argument(
        "--no-plot", action="store_true", help="No mostrar gráficos (solo texto)"
    )
    parser.add_argument("--list", action="store_true", help="Listar pares disponibles")
    parser.add_argument(
        "--verbose", action="store_true", help="Habilitar salida detallada (DEBUG)"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="png",
        choices=["png", "html", "both"],
        help="Formato de salida del gráfico (default: png)",
    )
    parser.add_argument(
        "--indicators", action="store_true", help="Incluir indicadores técnicos (RSI, MACD, SMA)"
    )
    parser.add_argument(
        "--predict", action="store_true", help="Generar proyecciones de tendencia y volatilidad"
    )
    return parser.parse_args()


def setup_logging(verbose: bool):
    """Configura el sistema de logging global."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s", force=True)


def list_pairs():
    logging.info("\n Pares de divisas disponibles:\n")
    for ticker, name in FOREX_PAIRS.items():
        print(f"  {ticker:<10} {name}")
    print()


def get_save_path(pair: str, period: str, fmt: str) -> str:
    """Genera una ruta de archivo consistente basada en el formato."""
    ext = "png" if fmt == "png" else "html"
    suffix = "analysis" if fmt == "png" else "interactive"
    return f"data/{pair}_{period}_{suffix}.{ext}"


def run_single_analysis(args):
    pair = args.pair.upper() if args.pair else _prompt_pair()
    analyzer = ForexVolatilityAnalyzer()

    report = analyzer.analyze(
        pair=pair,
        period=args.period,
        window=args.window,
        start_date=args.start,
        end_date=args.end,
        include_indicators=args.indicators,
    )

    print(report.summary())

    # --- Proyecciones ---
    if args.predict:
        predictor = ForexPredictor()
        projection = predictor.get_full_projection(report)
        trend = projection["trend"]
        vol = projection["volatility"]

        print("\n" + "═" * 55)
        print(f"   PROYECCIONES BÁSICAS — {pair}")
        print("═" * 55)
        print(f"  Tendencia ({trend['days']}d)    : {trend['trend']} ({trend['pct_change']:+.2f}%)")
        print(f"  Precio Proyectado        : {trend['projected_price']:.5f}")
        print(f"  Rango Esperado (ATR)     : {vol['expected_lower']:.5f} → {vol['expected_upper']:.5f}")
        print(f"  Variación Esperada       : {vol['range_pct']:.3f}%")
        print("═" * 55 + "\n")

    if not args.no_plot:
        save_png = get_save_path(pair, args.period, "png") if args.save else None
        save_html = get_save_path(pair, args.period, "html") if args.save else None

        if args.format == "png":
            plot_full_analysis(report, save_path=save_png, show=not args.save)
        elif args.format == "html":
            plot_interactive_analysis(report, save_path=save_html, show=not args.save)
        elif args.format == "both":
            plot_full_analysis(report, save_path=save_png, show=not args.save)
            plot_interactive_analysis(report, save_path=save_html, show=not args.save)


def run_comparison(args):
    analyzer = ForexVolatilityAnalyzer()

    pairs = args.pairs if args.pairs else list(FOREX_PAIRS.keys())
    logging.info(
        f"\n Comparando {len(pairs)} pares — período: {PERIODS[args.period]['label']}\n"
    )

    comparison = analyzer.compare_pairs(pairs, period=args.period, window=args.window)

    logging.info("\n Resumen comparativo (ordenado por volatilidad):\n")
    print(comparison.to_string())
    print()

    if not args.no_plot:
        save_path = f"data/comparison_{args.period}.png" if args.save else None
        plot_comparison(comparison, save_path=save_path, show=not args.save)


def _prompt_pair() -> str:
    """Modo interactivo si no se pasa --pair."""
    list_pairs()
    while True:
        pair = input("Ingresa el par de divisas (ej: EURUSD): ").strip().upper()
        if pair:
            return pair
        print("  Debes ingresar un par válido.")


def main():
    args = parse_args()
    setup_logging(args.verbose)

    if args.list:
        list_pairs()
        return

    if args.compare:
        run_comparison(args)
    else:
        run_single_analysis(args)


if __name__ == "__main__":
    main()
