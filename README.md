# Forex Volatility Dashboard

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

Plataforma moderna para el análisis y visualización de datos financieros obtenidos de Yahoo Finance, enfocada en la medición de volatilidad y análisis técnico avanzado de divisas.

## Características y Arquitectura

El proyecto está diseñado bajo una arquitectura estructurada (*Monorepo*), separando claramente la lógica de negocio y la presentación visual:

### Frontend
- Desarrollado con **Next.js** y **React**.
- Estilizado con **Tailwind CSS v4**, empleando efectos visuales modernos como *Glassmorphism*.
- Gráficos fluidos e interactivos con **Recharts** (Area charts con degradados, Bandas de Bollinger integradas).

### Backend
- API REST de alto rendimiento impulsada por **FastAPI**.
- Manejo de dependencias y entornos ultrarrápido gracias a **uv** (el gestor escrito en Rust).
- **Métricas Matemáticas:** Cálculo dinámico de volatilidad anualizada, Average True Range (ATR), Drawdowns, MACD y RSI mediante la potente librería de Pandas.

## Instalación y Uso

Asegúrate de tener Node.js y [uv](https://github.com/astral-sh/uv) instalados en tu equipo.

### 1. Iniciar el Backend
```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```
La API estará esperando peticiones en `http://127.0.0.1:8000`.

### 2. Iniciar el Frontend
En una pestaña nueva de tu terminal:
```bash
cd frontend
npm install
npm run dev
```
Visita `http://localhost:3000` en tu navegador para ver el dashboard en acción.

## Roadmap (Próximos Pasos)

El proyecto se encuentra en activa evolución. Las próximas actualizaciones incluirán:

- [ ] **Datos en Tiempo Real:** Integración de **WebSockets** para visualizar oscilaciones de precios al instante sin necesidad de recargar ni presionar botones de refresco.
- [ ] **Soporte para Criptomonedas:** Expansión del catálogo de análisis para incluir activos digitales (ej. BTC/USD, ETH/USD) conectando con múltiples *exchanges*.
- [ ] **Modelos Predictivos Avanzados:** Implementación de modelos de **Inteligencia Artificial y Machine Learning** para predecir tendencias y alertar sobre rupturas de volatilidad inminentes.
