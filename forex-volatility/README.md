#  Forex Volatility Analyzer

Herramienta en Python para analizar la **volatilidad y tendencia de pares de divisas** usando datos de [Yahoo Finance](https://finance.yahoo.com/). Genera métricas estadísticas, indicadores técnicos y visualizaciones interactivas.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![yfinance](https://img.shields.io/badge/data-Yahoo_Finance-720E9E)

---

##  Características

| Métrica / Herramienta | Descripción |
|---|---|
| **Volatilidad Histórica** | Desviación estándar de retornos logarítmicos (rolling) |
| **ATR** | Average True Range (Wilder) |
| **Bandas de Bollinger** | Media ± 2σ con BB Width |
| **RSI & MACD** | Indicadores de momentum y tendencia estándar de la industria |
| **Medias Móviles** | SMA y EMA (20, 50, 200 días) |
| **Predicciones** | Proyección de tendencia lineal y rango de volatilidad esperado |
| **Visualización** | Dashboards interactivos (Plotly) y estáticos (Matplotlib) |

---

##  Inicio Rápido

### 1. Clonar e instalar
```bash
git clone https://github.com/tu-usuario/forex-volatility.git
cd forex-volatility
pip install -r requirements.txt
```

### 2. Análisis completo (Interactivo + Indicadores + Predicciones)
```bash
python main.py --pair EURUSD --format html --indicators --predict
```

### 3. Comparar múltiples pares (Estático)
```bash
python main.py --compare --period 6m --format png
```

### 4. Guardar resultados en /data/
```bash
python main.py --pair USDCOP --format both --save
```

---

##  Uso en Python

```python
from src.volatility_analyzer import ForexVolatilityAnalyzer
from src.interactive_plotter import plot_interactive_analysis

analyzer = ForexVolatilityAnalyzer()

# Análisis completo con indicadores
report = analyzer.analyze("USDCOP", period="6m", include_indicators=True)
print(report.summary())

# Visualización interactiva
plot_interactive_//Sabor a código omitido para brevedad, pero se mantiene la estructura del archivo original actualizando imports...
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
  --format  FORMAT       Formato de salida: png | html | both (default: png)
  --indicators           Incluir RSI, MACD y Medias Móviles
  --predict              Generar proyecciones de tendencia y volatilidad
  --save                  Guardar gráficos en /data/
  --no-plot               Solo mostrar texto, sin gráficos
  --verbose               Habilitar logs de depuración (DEBUG)
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
│   ├── theme.py                # Centralización de colores y estilos
│   ├── volatility_analyzer.py  # Lógica principal: descarga + métricas
│   ├── plotter.py              # Visualizaciones estáticas (matplotlib)
│   ├── interactive_plotter.py  # Visualizaciones interactivas (plotly)
│   └── predictor.py            # Modelos de proyección
│
├── tests/
│   └── test_analyzer.py        # Tests unitarios (pytest)
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
| USDCOP | Dólar Americano / Peso Colombiano |
| ... | ... |

Cualquier par soportado por Yahoo Finance también funciona.

---

##  Disclaimer
Este proyecto es solo para fines **educativos y de análisis**. No constituye asesoría financiera ni recomendación de inversión.

---

##  Licencia
MIT License — ver [LICENSE](LICENSE)
