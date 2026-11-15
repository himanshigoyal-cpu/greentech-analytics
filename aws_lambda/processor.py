"""Shared core logic (identical copy lives in azure_function/). Standard library only."""
import csv, json, os, statistics, time, urllib.parse, urllib.request

OWM_URL = "https://api.openweathermap.org/data/2.5/weather"  # HTTPS only


def fetch_weather(city: str, api_key: str, timeout: int = 8) -> dict:
    """Source 1: live data from OpenWeatherMap (REST + JSON)."""
    qs = urllib.parse.urlencode({"q": city, "appid": api_key, "units": "metric"})
    with urllib.request.urlopen(f"{OWM_URL}?{qs}", timeout=timeout) as r:
        d = json.loads(r.read().decode())
    return {
        "city": d.get("name"),
        "temp_c": d["main"]["temp"],
        "humidity_pct": d["main"]["humidity"],
        "wind_ms": d.get("wind", {}).get("speed"),
        "conditions": d["weather"][0]["description"],
    }


def load_history(path: str) -> list[dict]:
    """Source 2: historical temperature + CO2 CSV (Kaggle Global Climate Change data)."""
    with open(path, newline="") as f:
        return [{"year": int(r["year"]), "avg_temp_c": float(r["avg_temp_c"]),
                 "co2_ppm": float(r["co2_ppm"])} for r in csv.DictReader(f)]


def analyze_history(rows: list[dict]) -> dict:
    years = [r["year"] for r in rows]
    temps = [r["avg_temp_c"] for r in rows]
    co2 = [r["co2_ppm"] for r in rows]
    slope = statistics.linear_regression(years, temps).slope
    return {
        "years": f"{min(years)}-{max(years)}",
        "mean_temp_c": round(statistics.mean(temps), 2),
        "warming_c_per_decade": round(slope * 10, 3),
        "co2_change_ppm": round(co2[-1] - co2[0], 1),
        "temp_co2_correlation": round(statistics.correlation(temps, co2), 3),
    }


def build_response(city: str, api_key: str | None, history_path: str, provider: str) -> dict:
    t0 = time.perf_counter()
    out = {"provider": provider, "history": analyze_history(load_history(history_path))}
    out["live"] = fetch_weather(city, api_key) if api_key else {"error": "OWM_API_KEY not set"}
    live = out["live"]
    if "temp_c" in live:
        out["comparison"] = {"live_minus_historical_mean_c":
                             round(live["temp_c"] - out["history"]["mean_temp_c"], 2)}
    out["processing_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return out