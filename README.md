# 서울 30년 기온 시계열 분석 (1995–2025)

서울의 일별 기온 11,323일치로 **추세·계절성·노이즈**를 분석하고, "서울은 어떻게 더워지고 있는가"에 대한 인사이트를 정리한 프로젝트입니다.

- 📄 **분석 리포트**: [REPORT.md](REPORT.md)
- 📓 **분석 코드**: [analysis.ipynb](analysis.ipynb) (실행 결과 포함)
- 📊 **대시보드 (보너스)**: [DASHBOARD.md](DASHBOARD.md)

- file:///C:/Users/SAMSUNG/OneDrive/%EB%B0%94%ED%83%95%20%ED%99%94%EB%A9%B4/m1/seoul-temperature-analysis/seoul-temperature-dashboard.html
- 
- 📘 **학습 가이드**: [학습가이드.md](학습가이드.md)

## 핵심 결과

| | |
|---|---|
| 연평균 기온 추세 | **+0.23℃ / 10년** (p = 0.031) |
| 가장 더운 해 | 2024년 (12.88℃), 2025년 (12.73℃) |
| 여름(6–8월) 변화 | **+0.93℃** (최근 10년 vs 초기 10년, p = 0.007) |
| 폭염일 (최고 ≥ 33℃) | 9일 (1995–2004) → **73일** (2015–2025) |
| 열대야 (최저 ≥ 25℃) | 4일 (1995–2004) → **83일** (2015–2025) |

## 폴더 구조

```
.
├── data/
│   ├── fetch_data.py                 # 데이터 수집 스크립트 (Open-Meteo API)
│   └── seoul_weather_1995_2025.csv   # 수집된 원본 데이터
├── images/                           # 분석 그래프 8개 (+ dashboard/ 스크린샷 4개)
├── dashboard/app.py                  # Streamlit 대시보드
├── analysis.ipynb                    # 분석 노트북
├── REPORT.md                         # 분석 리포트
├── DASHBOARD.md                      # 대시보드 실행법·시나리오
├── 학습가이드.md                      # 개념·코드 해설
└── requirements.txt                  # 라이브러리 목록
```

## 실행 방법

Python 3.11 이상이 필요합니다 (3.12.13에서 검증).

```bash
# 1. 가상환경 만들고 라이브러리 설치
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. 데이터 수집 (CSV가 이미 있으면 생략 가능)
python data/fetch_data.py

# 3. 분석 실행 → images/ 에 그래프 생성
jupyter nbconvert --to notebook --execute --inplace analysis.ipynb
#    또는: jupyter notebook 실행 후 analysis.ipynb 열고 Run All

# 4. 대시보드 (보너스)
streamlit run dashboard/app.py
```

## 데이터 출처 및 라이선스

- **Open-Meteo Historical Weather API** — https://open-meteo.com/en/docs/historical-weather-api
- 원천 데이터: **ERA5 / ERA5-Land 재분석 자료** (Copernicus Climate Change Service)
- 라이선스: **CC BY 4.0** — 출처를 표기하면 자유롭게 이용할 수 있습니다.
  > Weather data by Open-Meteo.com, based on ERA5 reanalysis (Copernicus Climate Change Service)
- 주의: 재분석 자료는 격자 평균값이라 기상청 관측소 공식 통계와 다를 수 있습니다 (특히 극한값).
