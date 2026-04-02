#  Forex Volatility Analyzer

Herramienta en Python para analizar la **volatilidad histórica de pares de divisas** usando datos de [Yahoo Finance](https://finance.yahoo.com/). Genera métricas estadísticas y visualizaciones detalladas.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![yfinance](https://img.shields.io/badge/data-Yahoo_Finance-720E9E)

---

##  Características

| Métrica | Descripción |
|---|---|
| **Volatilidad Histórica** | Desviación estándar de retornos logarítmicos (rolling) |
| **Volatilidad Anualizada** | Escala diaria × √252 |
| **ATR** | Average True Range (Wilder) |
| **Bandas de Bollinger** | Media ± 2σ con BB Width |
| **Drawdown** | Caída máxima desde el pico |
| **Retorno Acumulado** | Retorno total del período |

---

##  Inicio Rápido

### 1. Clonar e instalar

```bash
git clone https://github.com/tu-usuario/forex-volatility.git
cd forex-volatility
pip install -r requirements.txt
```

### 2. Análisis de un par

```bash
python main.py --pair EURUSD --period 3m
```

### 3. Comparar múltiples pares

```bash
python main.py --compare --period 6m
```

### 4. Guardar gráfico

```bash
python main.py --pair USDCOP --period 1y --save
```

---

##  Uso en Python

```python
from src.volatility_analyzer import ForexVolatilityAnalyzer
from src.plotter import plot_full_analysis, plot_comparison

analyzer = ForexVolatilityAnalyzer()

# ── Análisis de un par ─────────────────────────────────────────
report = analyzer.analyze("USDCOP", period="6m", window=20)
print(report.summary())

# ── Obtener métricas como diccionario ──────────────────────────
metrics = report.get_summary_dict()
print(f"Volatilidad anualizada: {metrics['volatility_annual_pct']:.2f}%")

# ── Visualización completa ────────────────────────────────────
plot_full_analysis(report, save_path="data/usdcop_analysis.png")

# ── Comparar múltiples pares ──────────────────────────────────
comparison = analyzer.compare_pairs(
    ["EURUSD", "GBPUSD", "USDMXN", "USDCOP", "USDBRL"],
    period="3m",
)
print(comparison)
plot_comparison(comparison, save_path="data/comparison.png")

# ── Rango de fechas personalizado ─────────────────────────────
report = analyzer.analyze(
    "EURUSD",
    start_date="2024-01-01",
    end_date="2024-12-31",
)
```

---

##  CLI — Referencia completa

```
python main.py [opciones]

Opciones:
  --pair     PAIR         Par de divisas (ej: EURUSD, USDCOP)
  --period   PERIOD       Período: 1w | 1m | 3m | 6m | 1y | 2y  (default: 3m)
  --window   N            Ventana rolling en días                 (default: 20)
  --start    YYYY-MM-DD   Fecha inicio personalizada
  --end      YYYY-MM-DD   Fecha fin personalizada
  --compare               Comparar múltiples pares
  --pairs    P1 P2 ...    Pares específicos para --compare
  --save                  Guardar gráficos en /data/
  --no-plot               Solo mostrar texto, sin gráficos
  --list                  Listar pares disponibles
```

---

##  Estructura del Proyecto

```
forex-volatility/
├── main.py                     # Punto de entrada CLI
├── requirements.txt
├── README.md
│
├── src/
│   ├── volatility_analyzer.py  # Lógica principal: descarga + métricas
│   └── plotter.py              # Visualizaciones con matplotlib
│
├── tests/
│   └── test_analyzer.py        # Tests unitarios (pytest)
│
├── notebooks/
│   └── exploracion.ipynb       # Análisis exploratorio (opcional)
│
└── data/                       # Gráficos exportados (git-ignored)
```

---

##  Ejecutar Tests

```bash
pip install pytest
pytest tests/ -v
```

---

##  Pares Soportados

| Ticker | Par |
|---|---|
| EURUSD | Euro / Dólar Americano |
| GBPUSD | Libra Esterlina / Dólar Americano |
| USDJPY | Dólar Americano / Yen Japonés |
| USDCHF | Dólar Americano / Franco Suizo |
| AUDUSD | Dólar Australiano / Dólar Americano |
| USDCAD | Dólar Americano / Dólar Canadiense |
| NZDUSD | Dólar Neozelandés / Dólar Americano |
| USDMXN | Dólar Americano / Peso Mexicano |
| **USDCOP** | **Dólar Americano / Peso Colombiano** |
| USDBRL | Dólar Americano / Real Brasileño |
| USDCLP | Dólar Americano / Peso Chileno |
| USDARS | Dólar Americano / Peso Argentino |

Cualquier par soportado por Yahoo Finance también funciona (ej: `EURCOP`, `GBPMXN`).

---

##  Disclaimer

Este proyecto es solo para fines **educativos y de análisis**. No constituye asesoría financiera ni recomendación de inversión.

---

##  Licencia

MIT License — ver [LICENSE](LICENSE)
