"""
서울 기온 탐색 대시보드 (보너스 과제)

실행:  streamlit run dashboard/app.py
브라우저에서 http://localhost:8501 이 자동으로 열린다.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).resolve().parent.parent / "data" / "seoul_weather_1995_2025.csv"
BLUE, ORANGE, RED, MUTED = "#2a78d6", "#eb6834", "#e34948", "#9a9893"
VARS = {"일평균 기온": "temp_mean", "일최고 기온": "temp_max", "일최저 기온": "temp_min"}
DEFAULT_TH = {"temp_mean": 28.0, "temp_max": 33.0, "temp_min": 25.0}   # 폭염일=최고 33℃, 열대야=최저 25℃

st.set_page_config(page_title="서울 기온 30년 대시보드", layout="wide")


@st.cache_data
def load():
    return pd.read_csv(DATA, parse_dates=["date"]).set_index("date").sort_index()


df = load()

st.title("서울 기온 30년 탐색 대시보드 (1995–2025)")
st.caption("데이터: Open-Meteo Historical Weather API (ERA5 재분석, CC BY 4.0) · 서울시청 좌표 기준")

# ── 필터: 한 줄에 배치 ─────────────────────────────────────────
# URL로 초기 필터 지정 가능 (예: ?start=2015&end=2025&var=temp_min&ma=365&th=25)
qp = st.query_params
labels = list(VARS)
init_var = next((k for k, v in VARS.items() if v == qp.get("var")), labels[0])

c1, c2, c3, c4 = st.columns([2.2, 1.2, 1.2, 1.2])
years = c1.slider("기간(연도)", 1995, 2025, (int(qp.get("start", 1995)), int(qp.get("end", 2025))))
var_label = c2.selectbox("지표", labels, index=labels.index(init_var))
ma_win = c3.select_slider("이동평균 창(일)", options=[7, 30, 90, 365], value=int(qp.get("ma", 30)))
col = VARS[var_label]
init_th = float(qp["th"]) if "th" in qp and col == VARS[init_var] else DEFAULT_TH[col]
threshold = c4.number_input("극한일 기준 (℃ 이상)", value=init_th, step=0.5, key=f"th_{col}",
                            help="선택한 지표가 이 값 이상인 날을 셉니다. 폭염일=최고 33℃, 열대야=최저 25℃")

view = df.loc[str(years[0]):str(years[1]), col]
if len(view) < 365:
    st.warning("기간이 너무 짧습니다. 최소 1년 이상 선택해 주세요.")
    st.stop()

annual = view.groupby(view.index.year).mean()
slope = np.polyfit(annual.index, annual.values, 1)[0] if len(annual) >= 3 else float("nan")
extreme = (view >= threshold).groupby(view.index.year).sum()
YEAR_TICK = 1 if len(annual) <= 12 else 5   # 연도 축을 정수로 (2,018.5 같은 표기 방지)

# ── 핵심 지표 ─────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("데이터 포인트", f"{len(view):,}일")
k2.metric(f"기간 평균 ({var_label})", f"{view.mean():.2f}℃")
k3.metric("선형 추세", f"{slope*10:+.2f}℃ / 10년" if not np.isnan(slope) else "–",
          help="연평균 값에 직선을 맞춘 기울기. 3년 이상 선택 시 계산")
k4.metric(f"{threshold:g}℃ 이상인 날", f"{int(extreme.sum())}일",
          help=f"연평균 {extreme.mean():.1f}일")

# ── 1. 일별 + 이동평균 ────────────────────────────────────────
st.subheader(f"① {var_label}와 {ma_win}일 이동평균")
fig = go.Figure()
fig.add_scatter(x=view.index, y=view, name="일별 값", line=dict(color=MUTED, width=0.6), opacity=0.6)
fig.add_scatter(x=view.index, y=view.rolling(ma_win, center=True).mean(),
                name=f"{ma_win}일 이동평균", line=dict(color=BLUE, width=2))
fig.update_layout(height=380, hovermode="x unified", yaxis_title="℃", margin=dict(t=10, b=10),
                  legend=dict(orientation="h", y=1.08))
st.plotly_chart(fig, width="stretch")

left, right = st.columns(2)

# ── 2. 연평균 + 추세선 ────────────────────────────────────────
with left:
    st.subheader("② 연평균과 선형 추세")
    fig = go.Figure()
    fig.add_scatter(x=annual.index, y=annual, mode="lines+markers", name="연평균",
                    line=dict(color=BLUE, width=2), marker=dict(size=8))
    if not np.isnan(slope):
        b = np.polyfit(annual.index, annual.values, 1)
        fig.add_scatter(x=annual.index, y=np.polyval(b, annual.index), name="추세선",
                        line=dict(color=ORANGE, width=2, dash="dash"))
    fig.update_layout(height=360, yaxis_title="℃", hovermode="x unified", margin=dict(t=10, b=10),
                      legend=dict(orientation="h", y=1.1), xaxis=dict(tickformat="d", dtick=YEAR_TICK))
    st.plotly_chart(fig, width="stretch")

# ── 3. 기준 이상 일수 ─────────────────────────────────────────
with right:
    st.subheader(f"③ 연도별 {threshold:g}℃ 이상인 날 수")
    fig = go.Figure(go.Bar(x=extreme.index, y=extreme, marker_color=ORANGE,
                           hovertemplate="%{x}년: %{y}일<extra></extra>"))
    fig.update_layout(height=360, yaxis_title="일수", margin=dict(t=10, b=10),
                      xaxis=dict(tickformat="d", dtick=YEAR_TICK))
    st.plotly_chart(fig, width="stretch")

# ── 4. 연도 × 월 편차 히트맵 ─────────────────────────────────
st.subheader("④ 연도×월 편차 (선택 기간의 같은 달 평균 대비)")
monthly = view.resample("MS").mean()
normal = monthly.groupby(monthly.index.month).transform("mean")
anom = (monthly - normal).to_frame("a")
grid = anom.assign(y=anom.index.year, m=anom.index.month).pivot(index="y", columns="m", values="a")
lim = float(np.nanmax(np.abs(grid.values)))
fig = go.Figure(go.Heatmap(
    z=grid.values, x=[f"{m}월" for m in grid.columns], y=grid.index,
    colorscale=[[0, BLUE], [0.5, "#f0efec"], [1, RED]], zmin=-lim, zmax=lim,
    colorbar=dict(title="℃"), xgap=2, ygap=2,
    hovertemplate="%{y}년 %{x}: %{z:+.2f}℃<extra></extra>"))
fig.update_layout(height=max(300, 22 * len(grid)), yaxis=dict(autorange="reversed", dtick=1),
                  margin=dict(t=10, b=10))
st.plotly_chart(fig, width="stretch")

with st.expander("표로 보기 (연도별 요약)"):
    st.dataframe(pd.DataFrame({"연평균(℃)": annual.round(2), f"{threshold:g}℃ 이상(일)": extreme}))
