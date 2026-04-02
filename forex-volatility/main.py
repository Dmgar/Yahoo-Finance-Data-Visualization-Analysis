#Punto de entrada CLI para el análisis de volatilidad de divisas.
"""
Uso:
    python main.py                              # Análisis interactivo
    python main.py --pair EURUSD --period 3m    # Análisis directo
    python main.py --compare --period 6m        # Comparar todos los pares
    python main.py --pair USDCOP --save         # Guardar gráfico
"""

import argparse
import sys
from pathlib import Path

# Asegurar que src/ esté en el path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from volatility_analyzer import ForexVolatilityAnalyzer, FOREX_PAIRS, PERIODS
from plotter import plot_full_analysis, plot_comparison


def parse_args():
    parser = argparse.ArgumentParser(
        description=" Análisis de Volatilidad de Divisas — Yahoo Finance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --pair EURUSD --period 3m
  python main.py --pair USDCOP --period 1y --window 30
  python main.py --compare --period 6m
  python main.py --pair GBPUSD --start 2024-01-01 --end 2024-12-31 --save
        """,
    )
    parser.add_argument("--pair",    type=str, help="Par de divisas (ej: EURUSD, USDCOP)")
    parser.add_argument("--period",  type=str, default="3m", choices=list(PERIODS.keys()), help="Período de análisis")
    parser.add_argument("--window",  type=int, default=20, help="Ventana para métricas rolling (default: 20)")
    parser.add_argument("--start",   type=str, help="Fecha inicio (YYYY-MM-DD)")
    parser.add_argument("--end",     type=str, help="Fecha fin (YYYY-MM-DD)")
    parser.add_argument("--compare", action="store_true", help="Comparar múltiples pares")
    parser.add_argument("--pairs",   type=str, nargs="+", help="Pares para comparar (con --compare)")
    parser.add_argument("--save",    action="store_true", help="Guardar gráficos en /data/")
    parser.add_argument("--no-plot", action="store_true", help="No mostrar gráficos (solo texto)")
    parser.add_argument("--list",    action="store_true", help="Listar pares disponibles")
    return parser.parse_args()


def list_pairs():
    print("\n Pares de divisas disponibles:\n")
    for ticker, name in FOREX_PAIRS.items():
        print(f"  {ticker:<10} {name}")
    print()


def run_single_analysis(args):
    pair = args.pair.upper() if args.pair else _prompt_pair()
    analyzer = ForexVolatilityAnalyzer()

    report = analyzer.analyze(
        pair=pair,
        period=args.period,
        window=args.window,
        start_date=args.start,
        end_date=args.end,
    )

    print(report.summary())

    if not args.no_plot:
        save_path = f"data/{pair}_{args.period}_analysis.png" if args.save else None
        plot_full_analysis(report, save_path=save_path, show=not args.save)


def run_comparison(args):
    analyzer = ForexVolatilityAnalyzer()

    pairs = args.pairs if args.pairs else list(FOREX_PAIRS.keys())
    print(f"\n Comparando {len(pairs)} pares — período: {PERIODS[args.period]['label']}\n")

    comparison = analyzer.compare_pairs(pairs, period=args.period, window=args.window)

    print("\n Resumen comparativo (ordenado por volatilidad):\n")
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

    if args.list:
        list_pairs()
        return

    if args.compare:
        run_comparison(args)
    else:
        run_single_analysis(args)


if __name__ == "__main__":
    main()
