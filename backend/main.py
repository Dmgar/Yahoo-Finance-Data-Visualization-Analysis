from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import math

from src.volatility_analyzer import ForexVolatilityAnalyzer, ForexDataError

app = FastAPI(title="Yahoo Finance Volatility API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    pair: str
    period: str = "3m"
    window: int = 20
    indicators: bool = True
    predict: bool = False

@app.get("/")
def read_root():
    return {"message": "Welcome to Yahoo Finance Volatility API"}

@app.post("/api/analyze")
def analyze_pair(request: AnalyzeRequest):
    try:
        analyzer = ForexVolatilityAnalyzer()
        report = analyzer.analyze(
            pair=request.pair,
            period=request.period,
            window=request.window,
            include_indicators=request.indicators
        )
        
        # Resumen general de métricas
        summary = report.get_summary_dict()
        
        # Convertir el DataFrame de datos históricos a un formato apto para JSON
        import numpy as np
        df = report.data.reset_index()
        df.rename(columns={"index": "Date"}, inplace=True, errors="ignore")
        df["Date"] = df["Date"].astype(str)
        
        # FastAPI y Pydantic tienen problemas con NaN o Inf, los pasamos a None de forma segura
        df = df.replace([np.nan, float('inf'), -float('inf')], None)
        
        chart_data = df.to_dict(orient="records")

        return {
            "pair": request.pair,
            "status": "success",
            "summary": summary,
            "chart_data": chart_data
        }
    except ForexDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
