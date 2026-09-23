"""
서울 일별 기상 데이터 수집 스크립트
- 출처: Open-Meteo Historical Weather API (https://open-meteo.com/en/docs/historical-weather-api)
- 원천 데이터: ERA5 / ERA5-Land 재분석 자료 (Copernicus Climate Change Service)
- 라이선스: CC BY 4.0 (출처 표기 시 자유 이용 가능)
- API 키 불필요

실행:  python data/fetch_data.py
결과:  data/seoul_weather_1995_2025.csv
"""
from pathlib import Path

import pandas as pd
import requests

URL = "https://archive-api.open-meteo.com/v1/archive"
PARAMS = {
    "latitude": 37.5665,        # 서울시청
    "longitude": 126.9780,
    "start_date": "1995-01-01",
    "end_date": "2025-12-31",
    "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,precipitation_sum",
    "timezone": "Asia/Seoul",
}
OUT = Path(__file__).parent / "seoul_weather_1995_2025.csv"


def main():
    resp = requests.get(URL, params=PARAMS, timeout=60)
    resp.raise_for_status()
    daily = resp.json()["daily"]

    df = pd.DataFrame(daily).rename(columns={
        "time": "date",
        "temperature_2m_mean": "temp_mean",
        "temperature_2m_max": "temp_max",
        "temperature_2m_min": "temp_min",
        "precipitation_sum": "precip",
    })
    df.to_csv(OUT, index=False)
    print(f"저장 완료: {OUT}  ({len(df):,}행, {df['date'].min()} ~ {df['date'].max()})")


if __name__ == "__main__":
    main()
