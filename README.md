#  Yahoo Finance Data Visualization & Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Análisis y visualización de datos financieros obtenidos de Yahoo Finance usando Python.

##  Características

### ✅ Implementado
- **Análisis de volatilidad de divisas (Forex):** Cálculo de volatilidad histórica, ATR, Bandas de Bollinger, Drawdown y Retorno acumulado.
- **Indicadores Técnicos Avanzados:** Implementación de RSI, MACD y Medias Móviles (SMA/EMA 20, 50, 200).
- **Visualizaciones Profesionales:** 
    - Gráficos estáticos detallados (Matplotlib).
    - Dashboards interactivos con velas japonesas y sincronización de ejes (Plotly).
- **Modelos Predictivos:** Proyecciones básicas de tendencia y rangos de volatilidad esperada.
- **Optimización:** Carga paralela de datos y sistema de logging profesional.
- **Descarga de datos:** Extracción automatizada de datos históricos desde Yahoo Finance.

### 🚀 Roadmap (En desarrollo)
- **Análisis fundamental:** Módulo para análisis de estados financieros de empresas.
- **Modelos predictivos avanzados:** Implementación de modelos de series temporales (ARIMA/LSTM).

##  Módulos

###  Forex Volatility Analyzer
Análisis de volatilidad y tendencia de pares de divisas.

| Archivo | Descripción |
|---|---|
| `forex-volatility/src/volatility_analyzer.py` | Lógica principal: descarga, métricas y técnicos |
| `forex-volatility/src/plotter.py` | Visualizaciones estáticas (Matplotlib) |
| `forex-volatility/src/interactive_plotter.py` | Dashboards interactivos (Plotly) |
| `forex-volatility/src/predictor.py` | Modelos de proyección y tendencia |
| `forex-volatility/main.py` | Punto de entrada CLI |

**Uso rápido:**
```bash
cd forex-volatility
pip install -r requirements.txt
python main.py --pair EURUSD --format html --indicators --predict
```

**Métricas incluidas:** Volatilidad histórica, ATR, Bandas de Bollinger, Drawdown, Retorno acumulado, RSI, MACD, SMA/EMA.

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
```
