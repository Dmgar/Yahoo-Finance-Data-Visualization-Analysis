import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Dict, Any
from volatility_analyzer import VolatilityReport


class ForexPredictor:
    """
    Provee proyecciones básicas basadas en tendencias lineales y volatilidad histórica.
    No constituye asesoría financiera.
    """

    def __init__(self, projection_days: int = 5):
        self.projection_days = projection_days

    def predict_trend(self, report: VolatilityReport) -> Dict[str, Any]:
        """
        Proyecta la tendencia del precio usando regresión lineal simple.
        """
        # Solo usamos la columna Close para evitar que NaN de otros indicadores vacíen el DF
        df_close = report.data[["Close"]].dropna()
        
        if len(df_close) < 2:
            return {"trend": "Insuficientes datos", "pct_change": 0, "projected_price": None, "days": self.projection_days}

        # Usamos los últimos 30 días disponibles
        recent_df = df_close.tail(30)
        
        X = np.arange(len(recent_df)).reshape(-1, 1)
        y = recent_df["Close"].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Proyección futura
        future_X = np.arange(len(recent_df), len(recent_df) + self.projection_days).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        current_price = y[-1]
        projected_price = predictions[-1]
        trend = "Alcista" if projected_price > current_price else "Bajista"
        pct_change = ((projected_price - current_price) / current_price) * 100
        
        return {
            "current_price": current_price,
            "projected_price": projected_price,
            "trend": trend,
            "pct_change": pct_change,
            "days": self.projection_days
        }

    def predict_volatility_range(self, report: VolatilityReport) -> Dict[str, Any]:
        """
        Calcula el rango esperado de movimiento basado en el ATR actual.
        """
        # Usamos solo las columnas necesarias para evitar que NaN de otros indicadores vacíen el DF
        df_subset = report.data[["Close", "atr"]].dropna()
        
        if df_subset.empty:
            return {"current_price": None, "atr": None, "expected_lower": None, "expected_upper": None, "range_pct": None}
            
        current_price = df_subset["Close"].iloc[-1]
        current_atr = df_subset["atr"].iloc[-1]
        
        # Rango esperado: Precio +/- ATR
        lower_bound = current_price - current_atr
        upper_bound = current_price + current_atr
        
        return {
            "current_price": current_price,
            "atr": current_atr,
            "expected_lower": lower_bound,
            "expected_upper": upper_bound,
            "range_pct": (current_atr / current_price) * 100
        }

    def get_full_projection(self, report: VolatilityReport) -> Dict[str, Any]:
        """
        Combina tendencia y volatilidad en un único reporte de proyección.
        """
        return {
            "trend": self.predict_trend(report),
            "volatility": self.predict_volatility_range(report),
        }
