


# 금융상품 시뮬레이션 대시보드

# Financial Market Simulation Dashboard - Advanced

## 🎓 프로젝트 개요

본 프로젝트는 "An Introduction to Global Financial Markets (8th Edition)" 교재를 기반으로, 60여 가지 금융상품의 **고급 시뮬레이션 기능**을 제공합니다.

### 주요 특징

#### 고급 기능 구현

**Phase A: 개별 상품 시뮬레이션 심화**
- ✅ **채권**: 수익률 곡선 변화 시뮬레이션 (Parallel Shift, Steepening, Flattening)
- ✅ **옵션**: 페이오프 다이어그램, 옵션 전략 빌더
- ✅ **선물**: 헤지 효과 시뮬레이션
- ✅ **금리 스왑**: 금리 시나리오별 현금흐름 분석
- ✅ VaR & CVaR (Conditional VaR) 계산

**Phase B: 포트폴리오 시뮬레이션 심화**
- ✅ **상관관계 히트맵** (Correlation Heatmap)
- ✅ **Sharpe Ratio & Sortino Ratio** 계산
- ✅ **스트레스 테스트** (2008 금융위기, 닷컴버블, 금리급등, 블랙스완, COVID-19)
- ✅ Historical VaR & Parametric VaR
- ✅ 효율적 투자선 (Efficient Frontier)

**Phase C: 구조화 상품 빌더**
- ✅ 옵션 전략 빌더 (Covered Call, Protective Put, Straddle, Strangle, Bull Call Spread)
- 🔄 ELS 시뮬레이터 (개발 예정)

### 기술 스택

**데이터 소스:**
- **yfinance**: Yahoo Finance API
- **FRED API**: 미국 국채 수익률 곡선 데이터

**프레임워크:**
- **Streamlit**: 웹 대시보드
- **Plotly**: 인터랙티브 차트

**분석 라이브러리:**
- pandas, numpy, scipy
- scikit-learn, statsmodels
- pypfopt, empyrical

**금융 모델:**
- Black-Scholes 옵션 가격 모델
- Geometric Brownian Motion (GBM)
- Markowitz 포트폴리오 이론
- Modern Portfolio Theory (MPT)

## 📦 설치 방법

### 1. 필수 요구사항
- Python 3.8 이상
- pip

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. (선택) FRED API 키 설정

수익률 곡선 기능을 사용하려면 FRED API 키가 필요합니다 (무료).

1. https://fred.stlouisfed.org/docs/api/api_key.html 에서 API 키 발급
2. 환경 변수 설정 (선택):
   ```bash
   export FRED_API_KEY="your_api_key_here"
   ```

> **Note**: FRED API 키가 없어도 샘플 수익률 곡선 데이터로 대시보드를 사용할 수 있습니다.

> 윈도우의 경우에는 아래와 같이 하셔야 합니다.

``` bash 
$env:FRED_API_KEY = "your_api_key_here"

```

### 4. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 대시보드를 확인할 수 있습니다.

## 프로젝트 구조

```
Financial_Market_Dashboard_Advanced/
├── app.py                          # Streamlit 메인 애플리케이션
├── requirements.txt                # 패키지 의존성
├── README.md                       # 프로젝트 문서
│
├── data/
│   └── data_fetcher.py            # yfinance + FRED 데이터 수집
│
├── simulations/
│   ├── individual_products.py     # 고급 개별 상품 시뮬레이터
│   │   ├── StockSimulator (VaR, CVaR)
│   │   ├── BondPricer (수익률 곡선 시뮬레이션)
│   │   ├── OptionPricer (전략 빌더)
│   │   ├── HedgeSimulator
│   │   └── InterestRateSwap
│   │
│   └── portfolio.py               # 고급 포트폴리오 시뮬레이터
│       ├── Sortino Ratio
│       ├── CVaR
│       ├── StressScenarios
│       └── 효율적 투자선
│
└── visualizations/
    ├── dashboards.py              # 메인 UI
    ├── dashboards_part1.py        # 주식 시뮬레이션
    ├── dashboards_part2.py        # 채권, 옵션, 헤지
    └── dashboards_part3.py        # 포트폴리오 분석
```

