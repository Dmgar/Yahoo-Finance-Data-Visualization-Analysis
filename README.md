#  Yahoo Finance Data Visualization & Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Análisis y visualización de datos financieros obtenidos de Yahoo Finance usando Python.

##  Características

-  Extracción de datos históricos y en tiempo real
-  Indicadores técnicos (RSI, MACD, medias móviles)
-  Visualizaciones interactivas con Plotly
-  Análisis fundamental de empresas
-  Modelos predictivos básicos
-  Análisis de volatilidad de divisas (Forex)
-  Métricas técnicas: ATR, Bandas de Bollinger, Drawdown

##  Módulos

###  Forex Volatility Analyzer
Análisis de volatilidad histórica de pares de divisas.

| Archivo | Descripción |
|---|---|
| `forex-volatility/src/volatility_analyzer.py` | Descarga datos y calcula métricas |
| `forex-volatility/src/plotter.py` | Visualizaciones con matplotlib |
| `forex-volatility/main.py` | Punto de entrada CLI |

**Uso rápido:**
```bash
cd forex-volatility
pip install -r requirements.txt
python main.py --pair EURUSD --period 3m
```

**Métricas incluidas:** Volatilidad histórica, ATR, Bandas de Bollinger, Drawdown, Retorno acumulado.

##  Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Dmgar/Yahoo-Finance-Data-Visualization-Analysis.git
cd Yahoo-Finance-Data-Visualization-Analysis

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
