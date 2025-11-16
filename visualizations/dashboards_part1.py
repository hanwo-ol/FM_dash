"""
고급 Streamlit 대시보드 렌더링 모듈
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from data.data_fetcher import DataFetcher
from simulations.individual_products import (
    StockSimulator, BondPricer, OptionPricer, 
    HedgeSimulator, InterestRateSwap
)
from simulations.portfolio import PortfolioSimulator, StressScenarios

def render_home():
    """홈 화면"""
    st.title("🏠 금융상품 시뮬레이션 대시보드 (석사급)")

    st.markdown("""
    ## 환영합니다!

    이 대시보드는 **석사급 퀄리티**의 금융상품 시뮬레이션과 분석을 제공합니다.

    ### 🎓 주요 고급 기능

    #### 📈 개별 상품 시뮬레이션
    - **주식**: Monte Carlo 시뮬레이션, VaR/CVaR 계산
    - **채권**: 수익률 곡선 변화 시뮬레이션 (Parallel, Steepening, Flattening)
    - **옵션**: Black-Scholes 모델, Greeks, 페이오프 다이어그램, 옵션 전략
    - **선물**: 헤지 효과 시뮬레이션
    - **금리 스왑**: 금리 시나리오별 현금흐름 분석

    #### 💼 포트폴리오 시뮬레이션
    - 효율적 투자선 (Efficient Frontier)
    - 포트폴리오 최적화
    - **상관관계 히트맵**
    - **Sharpe/Sortino Ratio**
    - **스트레스 테스트** (2008 금융위기, 닷컴버블 등)
    - Historical & Parametric VaR

    #### 🔧 구조화 상품 빌더
    - 옵션 전략 빌더 (Covered Call, Straddle, Strangle 등)
    - ELS 유사 상품 시뮬레이터

    ### 📊 데이터 소스
    - Yahoo Finance (yfinance)
    - FRED (Federal Reserve Economic Data) - 수익률 곡선

    ### 🚀 시작하기
    왼쪽 사이드바에서 원하는 메뉴를 선택하세요!
    """)

    # 주요 지수 현황
    st.markdown("### 📊 주요 지수 현황")

    col1, col2, col3 = st.columns(3)

    fetcher = DataFetcher()

    try:
        sp500 = fetcher.get_stock_data("^GSPC", period="5d")
        if not sp500.empty:
            latest = sp500['Close'].iloc[-1]
            change = ((sp500['Close'].iloc[-1] / sp500['Close'].iloc[-2]) - 1) * 100
            col1.metric("S&P 500", f"${latest:.2f}", f"{change:+.2f}%")
    except:
        col1.metric("S&P 500", "N/A")

    try:
        nasdaq = fetcher.get_stock_data("^IXIC", period="5d")
        if not nasdaq.empty:
            latest = nasdaq['Close'].iloc[-1]
            change = ((nasdaq['Close'].iloc[-1] / nasdaq['Close'].iloc[-2]) - 1) * 100
            col2.metric("NASDAQ", f"${latest:.2f}", f"{change:+.2f}%")
    except:
        col2.metric("NASDAQ", "N/A")

    try:
        kospi = fetcher.get_stock_data("^KS11", period="5d")
        if not kospi.empty:
            latest = kospi['Close'].iloc[-1]
            change = ((kospi['Close'].iloc[-1] / kospi['Close'].iloc[-2]) - 1) * 100
            col3.metric("KOSPI", f"{latest:.2f}", f"{change:+.2f}%")
    except:
        col3.metric("KOSPI", "N/A")


def render_individual_simulation():
    """개별 상품 시뮬레이션 화면"""
    st.title("📈 개별 상품 시뮬레이션 (고급)")

    tab1, tab2, tab3, tab4 = st.tabs(["📊 주식", "💰 채권 & 수익률 곡선", "📉 옵션 & 전략", "🔄 헤지 & 스왑"])

    # 주식 시뮬레이션
    with tab1:
        render_stock_simulation()

    # 채권 & 수익률 곡선
    with tab2:
        render_bond_yield_curve()

    # 옵션 & 전략
    with tab3:
        render_options_strategies()

    # 헤지 & 스왑
    with tab4:
        render_hedge_swap()


def render_stock_simulation():
    """주식 시뮬레이션"""
    st.header("주식 Monte Carlo 시뮬레이션")

    col1, col2 = st.columns([1, 2])

    with col1:
        ticker = st.text_input("티커 입력", value="AAPL")

        if st.button("데이터 조회"):
            fetcher = DataFetcher()
            data = fetcher.get_stock_data(ticker, period="1y")

            if not data.empty:
                st.session_state['stock_data'] = data
                st.session_state['ticker'] = ticker
                st.success(f"{ticker} 데이터 조회 완료!")

    if 'stock_data' in st.session_state:
        with col1:
            st.markdown("### 시뮬레이션 파라미터")
            S0 = st.number_input("초기 주가", value=float(st.session_state['stock_data']['Close'].iloc[-1]))
            mu = st.slider("기대 수익률 (연율)", -0.5, 0.5, 0.1, 0.01)
            sigma = st.slider("변동성 (연율)", 0.1, 1.0, 0.3, 0.05)
            T = st.slider("시뮬레이션 기간 (년)", 0.1, 5.0, 1.0, 0.1)
            n_sims = st.slider("시뮬레이션 횟수", 100, 5000, 1000, 100)

            if st.button("시뮬레이션 실행"):
                simulator = StockSimulator(S0, mu, sigma, T)
                paths = simulator.simulate(n_sims)
                var = simulator.calculate_var(paths)
                cvar = simulator.calculate_cvar(paths)

                st.session_state['sim_paths'] = paths
                st.session_state['var'] = var
                st.session_state['cvar'] = cvar

        with col2:
            # 실제 주가 차트
            st.markdown("### 과거 주가 추이")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=st.session_state['stock_data'].index,
                y=st.session_state['stock_data']['Close'],
                mode='lines',
                name='종가'
            ))
            fig.update_layout(
                xaxis_title="날짜",
                yaxis_title="주가",
                hovermode='x unified'
            )
            st.plotly_chart(fig, width='stretch')  # ✅ warning 해결

            # 시뮬레이션 결과
            if 'sim_paths' in st.session_state:
                st.markdown("### 시뮬레이션 결과")

                fig2 = go.Figure()

                for i in range(min(100, st.session_state['sim_paths'].shape[0])):
                    fig2.add_trace(go.Scatter(
                        y=st.session_state['sim_paths'][i],
                        mode='lines',
                        line=dict(width=0.5, color='lightblue'),
                        showlegend=False,
                        hoverinfo='skip'
                    ))

                mean_path = np.mean(st.session_state['sim_paths'], axis=0)
                fig2.add_trace(go.Scatter(
                    y=mean_path,
                    mode='lines',
                    line=dict(width=3, color='red'),
                    name='평균'
                ))

                fig2.update_layout(
                    title="Monte Carlo 시뮬레이션 경로",
                    xaxis_title="시간 (일)",
                    yaxis_title="주가",
                    hovermode='x unified'
                )
                st.plotly_chart(fig2, width='stretch')  # ✅ warning 해결

                # VaR & CVaR 표시
                col_a, col_b = st.columns(2)
                col_a.metric("VaR (95%)", f"{st.session_state['var']*100:.2f}%")
                col_b.metric("CVaR (95%)", f"{st.session_state['cvar']*100:.2f}%")
