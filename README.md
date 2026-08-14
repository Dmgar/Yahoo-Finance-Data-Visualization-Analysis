#  Yahoo Finance Data Visualization & Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Análisis y visualización de datos financieros obtenidos de Yahoo Finance usando Python.

##  Características

### ✅ Implementado
- **Análisis de volatilidad de divisas (Forex):** Cálculo de volatilidad histórica, ATR, Bandas de Bollinger, Drawdown y Retorno acumulado.
- **Descarga de datos:** Extracción automatizada de datos históricos desde Yahoo Finance.
- **Visualizaciones:** Gráficos detallados de análisis y comparativas entre múltiples pares.
- **Carga Paralela:** Optimización en la descarga de múltiples activos.

### 🚀 Roadmap (En desarrollo)
- **Indicadores técnicos:** Implementación de RSI, MACD y medias móviles.
- **Visualizaciones interactivas:** Migración a Plotly para análisis dinámicos.
- **Análisis fundamental:** Módulo para análisis de estados financieros de empresas.
- **Modelos predictivos:** Implementación de modelos básicos de predicción de precios.

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
