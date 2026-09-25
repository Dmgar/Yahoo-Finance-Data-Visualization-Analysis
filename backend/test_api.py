import json
import sys
from src.volatility_analyzer import ForexVolatilityAnalyzer

analyzer = ForexVolatilityAnalyzer()
try:
    report = analyzer.analyze(pair="EURUSD", period="1w", window=20, include_indicators=True)
    summary = report.get_summary_dict()
    print("Summary:", summary)
    
    import numpy as np
    df = report.data.reset_index()
    df.rename(columns={"index": "Date"}, inplace=True, errors="ignore")
    df["Date"] = df["Date"].astype(str)
    
    df = df.replace([np.nan, float('inf'), -float('inf')], None)
    chart_data = df.to_dict(orient="records")
    
    print("Data length:", len(chart_data))
except Exception as e:
    print(f"Error testing 1w: {e}")
