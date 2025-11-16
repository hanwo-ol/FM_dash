"""
고급 데이터 수집 모듈 (Yahoo Finance + FRED)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataFetcher:
    """yfinance + FRED를 사용한 시장 데이터 수집 클래스"""

    def __init__(self, fred_api_key=None):
        self.cache = {}
        self.fred_api_key = fred_api_key

        # FRED API 초기화 (키가 있는 경우)
        if fred_api_key:
            try:
                from fredapi import Fred
                self.fred = Fred(api_key=fred_api_key)
            except:
                self.fred = None
                print("Warning: FRED API 초기화 실패. 수익률 곡선 기능이 제한됩니다.")
        else:
            self.fred = None

    def get_stock_data(self, ticker, period="1y", interval="1d"):
        """주식 데이터 조회"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, interval=interval)
            return data
        except Exception as e:
            print(f"데이터 조회 오류: {e}")
            return pd.DataFrame()

    def get_multiple_stocks(self, tickers, period="1y", interval="1d"):
        """여러 주식 데이터 동시 조회"""
        data_dict = {}
        for ticker in tickers:
            data_dict[ticker] = self.get_stock_data(ticker, period, interval)
        return data_dict

    def get_stock_info(self, ticker):
        """주식 기본 정보 조회"""
        try:
            stock = yf.Ticker(ticker)
            return stock.info
        except Exception as e:
            print(f"정보 조회 오류: {e}")
            return {}

    def get_options_chain(self, ticker):
        """옵션 체인 데이터 조회"""
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options
            if len(expirations) > 0:
                opt = stock.option_chain(expirations[0])
                return opt.calls, opt.puts
            return pd.DataFrame(), pd.DataFrame()
        except Exception as e:
            print(f"옵션 데이터 조회 오류: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def get_treasury_yields(self):
        """
        미국 국채 수익률 곡선 데이터 조회 (FRED)

        Returns:
        --------
        pd.DataFrame
            기간별 수익률 데이터
        """
        # FRED 시리즈 ID (미국 국채 수익률)
        yield_series = {
            '1M': 'DGS1MO',
            '3M': 'DGS3MO',
            '6M': 'DGS6MO',
            '1Y': 'DGS1',
            '2Y': 'DGS2',
            '3Y': 'DGS3',
            '5Y': 'DGS5',
            '7Y': 'DGS7',
            '10Y': 'DGS10',
            '20Y': 'DGS20',
            '30Y': 'DGS30'
        }

        if self.fred:
            try:
                yields = {}
                for maturity, series_id in yield_series.items():
                    data = self.fred.get_series(series_id, observation_start='2020-01-01')
                    yields[maturity] = data.iloc[-1] if not data.empty else np.nan

                return pd.Series(yields)
            except Exception as e:
                print(f"FRED 데이터 조회 오류: {e}")

        # FRED API가 없는 경우 샘플 데이터 반환
        print("Warning: FRED API 키가 없어 샘플 수익률 곡선을 사용합니다.")
        return pd.Series({
            '1M': 5.0, '3M': 5.2, '6M': 5.3, '1Y': 4.8,
            '2Y': 4.5, '3Y': 4.3, '5Y': 4.2, '7Y': 4.3,
            '10Y': 4.4, '20Y': 4.6, '30Y': 4.5
        })

    def calculate_returns(self, data, period='daily'):
        """수익률 계산"""
        if 'Close' in data.columns:
            if period == 'daily':
                return data['Close'].pct_change()
            elif period == 'weekly':
                return data['Close'].resample('W').last().pct_change()
            elif period == 'monthly':
                return data['Close'].resample('M').last().pct_change()
        return pd.Series()

    def calculate_volatility(self, data, window=30):
        """변동성 계산 (연율화)"""
        returns = self.calculate_returns(data)
        return returns.rolling(window=window).std() * np.sqrt(252)

    def calculate_correlation_matrix(self, returns_df):
        """상관관계 행렬 계산"""
        return returns_df.corr()
