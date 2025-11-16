"""
고급 개별 금융상품 시뮬레이션 모듈
"""

import numpy as np
import pandas as pd
from scipy.stats import norm

class StockSimulator:
    """주식 시뮬레이터 (Monte Carlo)"""

    def __init__(self, S0, mu, sigma, T, dt=1/252):
        self.S0 = S0
        self.mu = mu
        self.sigma = sigma
        self.T = T
        self.dt = dt
        self.n_steps = int(T / dt)

    def simulate(self, n_simulations=1000):
        """주가 경로 시뮬레이션"""
        np.random.seed(42)
        paths = np.zeros((n_simulations, self.n_steps + 1))
        paths[:, 0] = self.S0

        for t in range(1, self.n_steps + 1):
            z = np.random.standard_normal(n_simulations)
            paths[:, t] = paths[:, t-1] * np.exp(
                (self.mu - 0.5 * self.sigma**2) * self.dt + 
                self.sigma * np.sqrt(self.dt) * z
            )

        return paths

    def calculate_var(self, paths, confidence=0.95):
        """VaR 계산"""
        final_values = paths[:, -1]
        initial_value = self.S0
        returns = (final_values - initial_value) / initial_value
        var = -np.percentile(returns, (1 - confidence) * 100)
        return var

    def calculate_cvar(self, paths, confidence=0.95):
        """CVaR (Conditional VaR) 계산"""
        final_values = paths[:, -1]
        initial_value = self.S0
        returns = (final_values - initial_value) / initial_value
        var = -np.percentile(returns, (1 - confidence) * 100)
        # VaR를 초과하는 손실의 평균
        cvar = -returns[returns < -var].mean()
        return cvar


class BondPricer:
    """채권 가격 계산기 (수익률 곡선 시뮬레이션 포함)"""

    @staticmethod
    def price_bond(face_value, coupon_rate, ytm, periods, frequency=2):
        """채권 가격 계산"""
        coupon = face_value * coupon_rate / frequency
        discount_rate = ytm / frequency

        pv_coupons = sum([coupon / (1 + discount_rate)**t for t in range(1, periods + 1)])
        pv_principal = face_value / (1 + discount_rate)**periods

        return pv_coupons + pv_principal

    @staticmethod
    def duration(face_value, coupon_rate, ytm, periods, frequency=2):
        """듀레이션 계산"""
        coupon = face_value * coupon_rate / frequency
        discount_rate = ytm / frequency

        price = BondPricer.price_bond(face_value, coupon_rate, ytm, periods, frequency)

        weighted_cf = 0
        for t in range(1, periods + 1):
            if t < periods:
                cf = coupon
            else:
                cf = coupon + face_value
            weighted_cf += (t / frequency) * cf / (1 + discount_rate)**t

        return weighted_cf / price

    @staticmethod
    def simulate_yield_curve_shift(base_yields, shift_type='parallel', magnitude=0.01):
        """
        수익률 곡선 변화 시뮬레이션

        Parameters:
        -----------
        base_yields : pd.Series
            기간별 기본 수익률
        shift_type : str
            'parallel', 'steepening', 'flattening'
        magnitude : float
            변화 크기 (예: 0.01 = 100bp)

        Returns:
        --------
        pd.Series
            변화된 수익률 곡선
        """
        maturities_months = {
            '1M': 1/12, '3M': 3/12, '6M': 6/12, '1Y': 1,
            '2Y': 2, '3Y': 3, '5Y': 5, '7Y': 7,
            '10Y': 10, '20Y': 20, '30Y': 30
        }

        shifted_yields = base_yields.copy()

        if shift_type == 'parallel':
            # 모든 만기에 동일한 변화
            shifted_yields = shifted_yields + magnitude

        elif shift_type == 'steepening':
            # 장기 금리가 더 많이 상승 (급경사화)
            for maturity in shifted_yields.index:
                years = maturities_months.get(maturity, 10)
                shift = magnitude * (years / 30)  # 30년 기준 정규화
                shifted_yields[maturity] += shift

        elif shift_type == 'flattening':
            # 단기 금리가 더 많이 상승 (평탄화)
            for maturity in shifted_yields.index:
                years = maturities_months.get(maturity, 10)
                shift = magnitude * (1 - years / 30)
                shifted_yields[maturity] += shift

        return shifted_yields


class OptionPricer:
    """옵션 가격 계산기 (Black-Scholes + 전략)"""

    @staticmethod
    def black_scholes(S, K, T, r, sigma, option_type='call'):
        """Black-Scholes 옵션 가격 계산"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        return price

    @staticmethod
    def greeks(S, K, T, r, sigma, option_type='call'):
        """Greeks 계산"""
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            delta = norm.cdf(d1)
        else:
            delta = -norm.cdf(-d1)

        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T)

        if option_type == 'call':
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                    - r * K * np.exp(-r * T) * norm.cdf(d2))
        else:
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))
                    + r * K * np.exp(-r * T) * norm.cdf(-d2))

        if option_type == 'call':
            rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        else:
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)

        return {
            'Delta': delta,
            'Gamma': gamma,
            'Vega': vega / 100,
            'Theta': theta / 365,
            'Rho': rho / 100
        }

    @staticmethod
    def payoff_diagram(S_range, K, option_type='call', premium=0, position='long'):
        """
        옵션 손익 다이어그램 계산

        Parameters:
        -----------
        S_range : np.ndarray
            기초자산 가격 범위
        K : float
            행사가격
        option_type : str
            'call' 또는 'put'
        premium : float
            옵션 프리미엄
        position : str
            'long' 또는 'short'

        Returns:
        --------
        np.ndarray
            손익 값
        """
        if option_type == 'call':
            intrinsic = np.maximum(S_range - K, 0)
        else:
            intrinsic = np.maximum(K - S_range, 0)

        if position == 'long':
            payoff = intrinsic - premium
        else:
            payoff = premium - intrinsic

        return payoff

    @staticmethod
    def strategy_payoff(S_range, legs):
        """
        복합 옵션 전략 손익 계산

        Parameters:
        -----------
        S_range : np.ndarray
            기초자산 가격 범위
        legs : list of dict
            전략 구성 요소
            예: [{'type': 'call', 'K': 100, 'premium': 5, 'position': 'long'}, ...]

        Returns:
        --------
        np.ndarray
            전체 전략 손익
        """
        total_payoff = np.zeros_like(S_range)

        for leg in legs:
            payoff = OptionPricer.payoff_diagram(
                S_range, 
                leg['K'], 
                leg['type'], 
                leg['premium'], 
                leg['position']
            )
            total_payoff += payoff

        return total_payoff


class HedgeSimulator:
    """헤지 시뮬레이터"""

    @staticmethod
    def stock_futures_hedge(stock_value, futures_price, contracts, stock_price_change):
        """
        주식 포지션의 선물 헤지 효과 시뮬레이션

        Parameters:
        -----------
        stock_value : float
            주식 포지션 가치
        futures_price : float
            선물 가격
        contracts : int
            선물 계약 수 (음수 = 매도)
        stock_price_change : float
            주가 변동률 (예: -0.1 = -10%)

        Returns:
        --------
        dict
            헤지 전후 손익
        """
        # 주식 손익
        stock_pl = stock_value * stock_price_change

        # 선물 손익 (베타를 1로 가정)
        futures_pl = contracts * futures_price * stock_price_change

        # 총 손익
        total_pl = stock_pl + futures_pl

        return {
            'stock_pl': stock_pl,
            'futures_pl': futures_pl,
            'total_pl': total_pl,
            'hedge_efficiency': abs(futures_pl / stock_pl) if stock_pl != 0 else 0
        }


class InterestRateSwap:
    """금리 스왑 시뮬레이터"""

    @staticmethod
    def calculate_cashflows(notional, fixed_rate, floating_rates, periods):
        """
        IRS 현금흐름 계산

        Parameters:
        -----------
        notional : float
            명목원금
        fixed_rate : float
            고정금리 (연율)
        floating_rates : list
            각 기간의 변동금리 (연율)
        periods : int
            지급 횟수

        Returns:
        --------
        pd.DataFrame
            기간별 현금흐름
        """
        cashflows = []

        for i in range(periods):
            fixed_payment = notional * fixed_rate
            floating_payment = notional * floating_rates[i] if i < len(floating_rates) else notional * floating_rates[-1]
            net_payment = fixed_payment - floating_payment

            cashflows.append({
                'Period': i + 1,
                'Fixed_Payment': fixed_payment,
                'Floating_Payment': floating_payment,
                'Net_Payment': net_payment
            })

        return pd.DataFrame(cashflows)
