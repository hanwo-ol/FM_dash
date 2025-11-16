"""
금융상품 시뮬레이션 대시보드 (석사급)
Financial Market Simulation Dashboard - Advanced
"""

import streamlit as st
import sys
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from visualizations.dashboards import (
    render_home, 
    render_individual_simulation, 
    render_portfolio_simulation, 
    render_product_builder
)

# 페이지 설정
st.set_page_config(
    page_title="금융상품 시뮬레이션 대시보드 (석사급)",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 메뉴
st.sidebar.title("📊 금융 시뮬레이션 (석사급)")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "🏠 홈",
        "📈 개별 상품 시뮬레이션",
        "💼 포트폴리오 시뮬레이션",
        "🔧 구조화 상품 빌더"
    ]
)

st.sidebar.markdown("---")

# 고급 기능 안내
st.sidebar.success(
    """
    **🎓 석사급 기능**

    ✅ 수익률 곡선 시뮬레이션
    ✅ 옵션 전략 빌더
    ✅ 상관관계 히트맵
    ✅ Sharpe/Sortino Ratio
    ✅ 스트레스 테스트
    ✅ 헤지 시뮬레이션
    ✅ 금리 스왑 분석
    """
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **데이터 소스**:
    - Yahoo Finance (yfinance)
    - FRED (수익률 곡선)

    **지원 상품**:
    - 주식, 채권, 옵션, 선물, 외환
    - 금리 스왑, 구조화 상품
    """
)

# 메뉴에 따른 화면 렌더링
if menu == "🏠 홈":
    render_home()
elif menu == "📈 개별 상품 시뮬레이션":
    render_individual_simulation()
elif menu == "💼 포트폴리오 시뮬레이션":
    render_portfolio_simulation()
elif menu == "🔧 구조화 상품 빌더":
    render_product_builder()

# 푸터
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Financial Market Dashboard (Advanced)")
st.sidebar.markdown("**석사급 프로젝트**")
