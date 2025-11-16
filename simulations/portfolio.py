"""
고급 포트폴리오 시뮬레이션 모듈
"""

import numpy as np
import pandas as pd
from scipy.stats import norm

class PortfolioSimulator:
    """포트폴리오 시뮬레이터 (고급)"""

    def __init__(self, returns, weights=None):
        self.returns = returns
        self.n_assets = len(returns.columns)

        if weights is None:
            self.weights = np.array([1/self.n_assets] * self.n_assets)
        else:
            self.weights = np.array(weights)

    def calculate_portfolio_metrics(self):
        """포트폴리오 성과 지표 계산"""
        portfolio_return = np.sum(self.returns.mean() * self.weights) * 252
        cov_matrix = self.returns.cov() * 252
        portfolio_std = np.sqrt(np.dot(self.weights.T, np.dot(cov_matrix, self.weights)))
        sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0

        return {
            'return': portfolio_return,
            'volatility': portfolio_std,
            'sharpe_ratio': sharpe_ratio
        }

    def calculate_sortino_ratio(self, target_return=0):
        """
        소르티노 비율 계산

        Parameters:
        -----------
        target_return : float
            목표 수익률 (연율)

        Returns:
        --------
        float
            Sortino Ratio
        """
        portfolio_returns = (self.returns * self.weights).sum(axis=1)
        excess_return = portfolio_returns.mean() * 252 - target_return

        # 하방 편차 (downside deviation)
        downside_returns = portfolio_returns[portfolio_returns < target_return/252]
        downside_std = downside_returns.std() * np.sqrt(252)

        sortino_ratio = excess_return / downside_std if downside_std > 0 else 0
        return sortino_ratio

    def efficient_frontier(self, n_portfolios=10000):
        """효율적 투자선 계산"""
        np.random.seed(42)

        results = np.zeros((4, n_portfolios))
        all_weights = []

        for i in range(n_portfolios):
            weights = np.random.random(self.n_assets)
            weights /= np.sum(weights)
            all_weights.append(weights)

            portfolio_return = np.sum(self.returns.mean() * weights) * 252
            cov_matrix = self.returns.cov() * 252
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0

            results[0,i] = portfolio_return
            results[1,i] = portfolio_std
            results[2,i] = sharpe_ratio
            results[3,i] = i

        results_df = pd.DataFrame(results.T, columns=['return', 'volatility', 'sharpe', 'index'])
        results_df['weights'] = all_weights

        return results_df

    def optimize_portfolio(self, target='max_sharpe'):
        """포트폴리오 최적화"""
        frontier = self.efficient_frontier()

        if target == 'max_sharpe':
            idx = frontier['sharpe'].idxmax()
        else:
            idx = frontier['volatility'].idxmin()

        optimal = frontier.loc[idx]

        return {
            'weights': optimal['weights'],
            'return': optimal['return'],
            'volatility': optimal['volatility'],
            'sharpe_ratio': optimal['sharpe']
        }

    def calculate_var(self, confidence=0.95, method='historical'):
        """포트폴리오 VaR 계산"""
        portfolio_returns = (self.returns * self.weights).sum(axis=1)

        if method == 'historical':
            var = -np.percentile(portfolio_returns, (1 - confidence) * 100)
        else:
            mean = portfolio_returns.mean()
            std = portfolio_returns.std()
            var = -(mean + norm.ppf(1 - confidence) * std)

        return var

    def calculate_cvar(self, confidence=0.95):
        """
        CVaR (Conditional VaR / Expected Shortfall) 계산

        Returns:
        --------
        float
            CVaR 값
        """
        portfolio_returns = (self.returns * self.weights).sum(axis=1)
        var = -np.percentile(portfolio_returns, (1 - confidence) * 100)

        # VaR를 초과하는 손실의 평균
        cvar = -portfolio_returns[portfolio_returns < -var].mean()
        return cvar

    def stress_test(self, scenario_name, shock_magnitudes):
        """
        스트레스 테스트

        Parameters:
        -----------
        scenario_name : str
            시나리오 이름
        shock_magnitudes : dict or list
            자산별 충격 크기 (예: {'AAPL': -0.3, 'MSFT': -0.25})

        Returns:
        --------
        dict
            스트레스 테스트 결과
        """
        if isinstance(shock_magnitudes, dict):
            shocks = [shock_magnitudes.get(col, 0) for col in self.returns.columns]
        else:
            shocks = shock_magnitudes

        # 포트폴리오 가치 변화
        portfolio_shock = np.dot(self.weights, shocks)

        return {
            'scenario': scenario_name,
            'portfolio_shock': portfolio_shock,
            'individual_shocks': dict(zip(self.returns.columns, shocks))
        }


class StressScenarios:
    """역사적/가상 스트레스 시나리오"""

    @staticmethod
    def get_scenarios():
        """사전 정의된 스트레스 시나리오 반환"""
        return {
            '2008_financial_crisis': {
                'name': '2008 금융위기',
                'description': '서브프라임 모기지 사태로 인한 글로벌 금융위기',
                'equity_shock': -0.40,    # 주식 -40%
                'bond_shock': 0.10,       # 채권 +10% (안전자산 선호)
                'real_estate_shock': -0.35,
                'commodity_shock': -0.30
            },
            'dotcom_bubble': {
                'name': '닷컴 버블 붕괴',
                'description': '2000년대 초 인터넷 기업 버블 붕괴',
                'equity_shock': -0.50,
                'tech_shock': -0.70,      # 기술주 -70%
                'bond_shock': 0.05,
                'commodity_shock': -0.10
            },
            'rate_hike': {
                'name': '급격한 금리 인상',
                'description': '중앙은행의 급격한 기준금리 인상',
                'equity_shock': -0.20,
                'bond_shock': -0.15,      # 채권 가격 하락
                'real_estate_shock': -0.25,
                'commodity_shock': -0.10
            },
            'black_swan': {
                'name': '블랙 스완 이벤트',
                'description': '예측 불가능한 극단적 시장 충격',
                'equity_shock': -0.60,
                'bond_shock': 0.15,
                'commodity_shock': -0.40,
                'volatility_spike': 3.0   # 변동성 3배 증가
            },
            'covid19_crash': {
                'name': 'COVID-19 팬데믹',
                'description': '2020년 코로나19로 인한 시장 급락',
                'equity_shock': -0.35,
                'travel_shock': -0.60,    # 여행/관광 -60%
                'tech_shock': 0.20,       # 기술주 +20%
                'bond_shock': 0.05
            }
        }
