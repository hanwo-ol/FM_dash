# 금융상품 시뮬레이션 대시보드 

# Financial Market Simulation Dashboard - Advanced

## 🎓 프로젝트 개요

본 프로젝트는 "An Introduction to Global Financial Markets (8th Edition)" 교재를 기반으로, 60여 가지 금융상품의 **고급 시뮬레이션 기능**을 제공합니다.

### 주요 특징

#### 🔥 고급 기능 구현

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

### 🛠️ 기술 스택

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

### 4. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 대시보드를 확인할 수 있습니다.

## 📂 프로젝트 구조

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

## 🎯 주요 기능

### 1. 개별 상품 시뮬레이션

#### 주식
- Monte Carlo 시뮬레이션 (GBM)
- VaR (95% 신뢰수준)
- CVaR (Expected Shortfall)

#### 채권
- 채권 가격 계산
- Macaulay Duration
- **수익률 곡선 변화 시뮬레이션**
  - Parallel Shift: 모든 만기 동일 변화
  - Steepening: 장기 금리 상승폭 > 단기
  - Flattening: 단기 금리 상승폭 > 장기

#### 옵션
- Black-Scholes 가격 계산
- Greeks (Delta, Gamma, Vega, Theta, Rho)
- **페이오프 다이어그램**
- **옵션 전략 빌더**
  - Covered Call
  - Protective Put
  - Straddle
  - Strangle
  - Bull Call Spread

#### 헤지 & 스왑
- **선물 헤지 시뮬레이션**: 주식 포지션의 선물 헤지 효과
- **금리 스왑**: 고정금리 vs 변동금리 현금흐름 분석

### 2. 포트폴리오 시뮬레이션

#### 기본 분석
- 포트폴리오 수익률 & 변동성
- Sharpe Ratio
- **Sortino Ratio** (하방 리스크 고려)

#### 리스크 분석
- **상관관계 히트맵** (Plotly 인터랙티브)
- Historical VaR
- Parametric VaR
- **CVaR (Expected Shortfall)**

#### 최적화
- 효율적 투자선 (Efficient Frontier)
- 최대 Sharpe Ratio 포트폴리오
- 최소 변동성 포트폴리오

#### 스트레스 테스트
사전 정의된 역사적 위기 시나리오:
- **2008 금융위기** (주식 -40%)
- **닷컴 버블** (기술주 -70%)
- **급격한 금리 인상** (채권 -15%)
- **블랙 스완 이벤트** (주식 -60%)
- **COVID-19 팬데믹** (여행 -60%, 기술주 +20%)

### 3. 구조화 상품 빌더

- 옵션 전략 조합
- 커스텀 전략 구성
- 페이오프 다이어그램 시각화

## 🔧 사용 예시

### 수익률 곡선 시뮬레이션

```python
from simulations.individual_products import BondPricer

# 기본 수익률 곡선
base_yields = pd.Series({
    '1Y': 4.5, '2Y': 4.3, '5Y': 4.2,
    '10Y': 4.4, '30Y': 4.5
})

# Steepening (급경사화) 시뮬레이션
shifted_yields = BondPricer.simulate_yield_curve_shift(
    base_yields,
    shift_type='steepening',
    magnitude=0.01  # 100bp
)
```

### 옵션 전략 빌더

```python
from simulations.individual_products import OptionPricer

# Straddle 전략
legs = [
    {'type': 'call', 'K': 100, 'premium': 5, 'position': 'long'},
    {'type': 'put', 'K': 100, 'premium': 5, 'position': 'long'}
]

S_range = np.linspace(50, 150, 100)
payoff = OptionPricer.strategy_payoff(S_range, legs)
```

### 스트레스 테스트

```python
from simulations.portfolio import PortfolioSimulator, StressScenarios

portfolio = PortfolioSimulator(returns, weights)

# 2008 금융위기 시나리오
scenarios = StressScenarios.get_scenarios()
crisis_scenario = scenarios['2008_financial_crisis']

result = portfolio.stress_test(
    crisis_scenario['name'],
    shock_magnitudes=[-0.40] * n_assets
)
```

## 📊 개선 사항 (vs 기본 버전)

### ✅ 해결된 문제
1. **Streamlit Warning 해결**: `use_container_width` → `width='stretch'`
2. **FRED API 통합**: 실제 수익률 곡선 데이터
3. **고급 리스크 지표**: CVaR, Sortino Ratio 추가
4. **상관관계 분석**: 히트맵 시각화
5. **스트레스 테스트**: 5가지 역사적 시나리오
6. **옵션 전략 빌더**: 6가지 사전 정의 전략
7. **헤지 시뮬레이터**: 선물 헤지 효과 분석
8. **금리 스왑 분석**: 현금흐름 시뮬레이션

### 🆕 추가된 기능
- 수익률 곡선 변화 시뮬레이션 (Parallel, Steepening, Flattening)
- 옵션 페이오프 다이어그램
- Sortino Ratio (하방 리스크 조정 수익률)
- CVaR (Expected Shortfall)
- 상관관계 히트맵
- 스트레스 테스트 시나리오

## 🚀 향후 개발 계획

### Phase 4 (단기)
- [ ] 외환 시뮬레이터 (금리평가설, Carry Trade)
- [ ] Binomial Tree 옵션 가격 모델
- [ ] 내재변동성 (Implied Volatility) 계산

### Phase 5 (중기)
- [ ] ELS 시뮬레이터 (넉인 배리어, 조기상환)
- [ ] Exotic 옵션 (Asian, Barrier, Rainbow)
- [ ] Credit Default Swap (CDS) 시뮬레이터

### Phase 6 (장기)
- [ ] 백테스팅 엔진
- [ ] 실시간 데이터 스트리밍
- [ ] 머신러닝 기반 예측 모델
- [ ] 포트폴리오 리밸런싱 최적화

## 📚 참고 자료

**교재:**
- Valdez, S., & Molyneux, P. (2016). *An Introduction to Global Financial Markets* (8th ed.). Palgrave Macmillan.

**금융 모델:**
- Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities. *Journal of Political Economy*.
- Markowitz, H. (1952). Portfolio Selection. *The Journal of Finance*.
- Hull, J. C. (2018). *Options, Futures, and Other Derivatives* (10th ed.). Pearson.

**라이브러리:**
- yfinance: https://github.com/ranaroussi/yfinance
- FRED API: https://fred.stlouisfed.org/docs/api/
- Streamlit: https://streamlit.io
- Plotly: https://plotly.com/python

## 💡 Troubleshooting

### FRED API 오류
- API 키가 없어도 샘플 데이터로 작동합니다
- 정식 수익률 곡선 데이터가 필요하면 FRED API 키를 발급받으세요

### yfinance 데이터 오류
- 일부 티커는 Yahoo Finance에서 지원하지 않을 수 있습니다
- 미국 주식 (AAPL, MSFT 등)과 주요 지수 (^GSPC, ^IXIC 등)는 안정적으로 작동합니다

## 📝 라이선스

이 프로젝트는 교육 목적으로 개발되었습니다.

---

**© 2025 Financial Market Dashboard (Advanced)**
#   F M _ d a s h 
 
 
