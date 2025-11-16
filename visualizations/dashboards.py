"""
고급 Streamlit 대시보드 렌더링 모듈 (통합)
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
    """개별 상품 시뮬레이션 (간략 버전 - 전체는 별도 파일 참조)"""
    st.title("📈 개별 상품 시뮬레이션 (고급)")
    st.info("상세 기능은 dashboards_part1.py, dashboards_part2.py 파일을 참조하세요.")

    st.markdown("""
    ### 구현된 고급 기능:

    #### 주식
    - Monte Carlo 시뮬레이션
    - VaR & CVaR 계산

    #### 채권
    - 채권 가격 계산
    - **수익률 곡선 변화 시뮬레이션**
      - Parallel Shift
      - Steepening
      - Flattening

    #### 옵션
    - Black-Scholes 가격 계산
    - Greeks 계산
    - **페이오프 다이어그램**
    - **옵션 전략 빌더**
      - Covered Call
      - Protective Put
      - Straddle / Strangle
      - Bull Call Spread

    #### 선물 & 스왑
    - **헤지 시뮬레이션**
    - **금리 스왑 현금흐름 분석**
    """)


def render_portfolio_simulation():
    """포트폴리오 시뮬레이션 (간략 버전)"""
    st.title("💼 포트폴리오 시뮬레이션 (석사급)")
    st.info("상세 기능은 dashboards_part3.py 파일을 참조하세요.")

    st.markdown("""
    ### 구현된 고급 기능:

    #### 기본 분석
    - 포트폴리오 수익률 & 변동성
    - **Sharpe Ratio**
    - **Sortino Ratio**

    #### 리스크 분석
    - **상관관계 히트맵** (Plotly)
    - Historical VaR
    - Parametric VaR
    - CVaR (Expected Shortfall)

    #### 최적화
    - 효율적 투자선 (Efficient Frontier)
    - 최대 Sharpe Ratio 포트폴리오
    - 최소 변동성 포트폴리오

    #### 스트레스 테스트
    - **2008 금융위기**
    - **닷컴 버블**
    - **급격한 금리 인상**
    - **블랙 스완 이벤트**
    - **COVID-19 팬데믹**
    """)


def render_product_builder():
    """구조화 상품 빌더"""
    st.title("🔧 구조화 상품 빌더")

    st.markdown("""
    ### 🎓 옵션 전략 빌더

    다양한 옵션 조합 전략의 손익 구조를 시뮬레이션합니다.

    **지원 전략:**
    1. **Covered Call**: 주식 보유 + Call 옵션 매도
    2. **Protective Put**: 주식 보유 + Put 옵션 매수
    3. **Straddle**: Call + Put 동시 매수 (동일 행사가)
    4. **Strangle**: OTM Call + OTM Put 매수
    5. **Bull Call Spread**: ITM Call 매수 + OTM Call 매도
    6. **Bear Put Spread**: ITM Put 매수 + OTM Put 매도

    ### 🎓 ELS 시뮬레이터 (개발 예정)

    - 조기상환 조건 설정
    - 녹인/녹아웃 배리어
    - Monte Carlo 가격 계산
    - 페이오프 다이어그램
    """)

    st.info("전체 옵션 전략 기능은 dashboards_part2.py의 render_options_strategies()를 참조하세요.")
