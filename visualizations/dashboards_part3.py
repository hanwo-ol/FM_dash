
def render_portfolio_simulation():
    """포트폴리오 시뮬레이션 화면 (고급)"""
    st.title("💼 포트폴리오 시뮬레이션 (석사급)")

    st.markdown("### 포트폴리오 구성")

    tickers_input = st.text_input(
        "티커 입력 (쉼표로 구분)", 
        value="AAPL,MSFT,GOOGL,AMZN,TSLA"
    )
    tickers = [t.strip() for t in tickers_input.split(',')]

    period = st.selectbox("데이터 기간", ["6mo", "1y", "2y", "5y"], index=1)

    if st.button("데이터 조회 및 분석"):
        with st.spinner("데이터 조회 중..."):
            fetcher = DataFetcher()
            data_dict = fetcher.get_multiple_stocks(tickers, period=period)

            closes = pd.DataFrame()
            for ticker, data in data_dict.items():
                if not data.empty:
                    closes[ticker] = data['Close']

            if not closes.empty:
                returns = closes.pct_change().dropna()

                st.session_state['closes'] = closes
                st.session_state['returns'] = returns
                st.session_state['tickers'] = tickers
                st.success("데이터 조회 완료!")

    if 'returns' in st.session_state:
        returns = st.session_state['returns']
        tickers = st.session_state['tickers']

        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 기본 분석",
            "🔥 상관관계 & 리스크",
            "⚡ 효율적 투자선",
            "💥 스트레스 테스트"
        ])

        with tab1:
            render_portfolio_basic(returns, tickers)

        with tab2:
            render_correlation_risk(returns, tickers)

        with tab3:
            render_efficient_frontier(returns, tickers)

        with tab4:
            render_stress_test(returns, tickers)


def render_portfolio_basic(returns, tickers):
    """기본 포트폴리오 분석"""
    st.markdown("### 포트폴리오 가중치 설정")

    weights = []
    cols = st.columns(len(tickers))
    for i, ticker in enumerate(tickers):
        with cols[i]:
            w = st.slider(f"{ticker}", 0.0, 1.0, 1.0/len(tickers), 0.05, key=f"weight_{ticker}")
            weights.append(w)

    weights = np.array(weights)
    if weights.sum() > 0:
        weights = weights / weights.sum()

    st.info(f"정규화된 가중치: {', '.join([f'{t}: {w:.2%}' for t, w in zip(tickers, weights)])}")

    portfolio = PortfolioSimulator(returns, weights)
    metrics = portfolio.calculate_portfolio_metrics()
    sortino = portfolio.calculate_sortino_ratio()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("연간 수익률", f"{metrics['return']*100:.2f}%")
    col2.metric("연간 변동성", f"{metrics['volatility']*100:.2f}%")
    col3.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    col4.metric("Sortino Ratio", f"{sortino:.2f}")


def render_correlation_risk(returns, tickers):
    """상관관계 및 리스크 분석"""
    st.markdown("### 🎓 상관관계 히트맵")

    corr_matrix = returns.corr()

    # Plotly 히트맵
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="상관계수")
    ))

    fig.update_layout(
        title="자산 간 상관관계",
        xaxis_title="",
        yaxis_title="",
        width=700,
        height=600
    )

    st.plotly_chart(fig, width='stretch')  # ✅ warning 해결

    st.markdown("### 리스크 지표")

    # 가중치 입력 (간단히 동일 가중)
    weights = np.array([1/len(tickers)] * len(tickers))
    portfolio = PortfolioSimulator(returns, weights)

    col1, col2, col3 = st.columns(3)

    var_hist = portfolio.calculate_var(confidence=0.95, method='historical')
    var_param = portfolio.calculate_var(confidence=0.95, method='parametric')
    cvar = portfolio.calculate_cvar(confidence=0.95)

    col1.metric("Historical VaR (95%)", f"{var_hist*100:.2f}%")
    col2.metric("Parametric VaR (95%)", f"{var_param*100:.2f}%")
    col3.metric("CVaR (95%)", f"{cvar*100:.2f}%")


def render_efficient_frontier(returns, tickers):
    """효율적 투자선"""
    st.markdown("### 효율적 투자선 (Efficient Frontier)")

    if st.button("효율적 투자선 계산", key='ef_calc'):
        with st.spinner("계산 중..."):
            weights = np.array([1/len(tickers)] * len(tickers))
            portfolio = PortfolioSimulator(returns, weights)
            frontier = portfolio.efficient_frontier(n_portfolios=5000)
            st.session_state['frontier'] = frontier
            st.session_state['portfolio_obj'] = portfolio

    if 'frontier' in st.session_state:
        frontier = st.session_state['frontier']
        portfolio = st.session_state['portfolio_obj']

        # 현재 포트폴리오 지표
        metrics = portfolio.calculate_portfolio_metrics()

        fig = go.Figure()

        # 전체 포트폴리오
        fig.add_trace(go.Scatter(
            x=frontier['volatility']*100,
            y=frontier['return']*100,
            mode='markers',
            marker=dict(
                size=5,
                color=frontier['sharpe'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio")
            ),
            text=[f"수익률: {r:.2f}%<br>변동성: {v:.2f}%<br>Sharpe: {s:.2f}" 
                  for r, v, s in zip(frontier['return']*100, frontier['volatility']*100, frontier['sharpe'])],
            hovertemplate='%{text}<extra></extra>',
            name='포트폴리오'
        ))

        # 현재 포트폴리오
        fig.add_trace(go.Scatter(
            x=[metrics['volatility']*100],
            y=[metrics['return']*100],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star'),
            name='현재 포트폴리오'
        ))

        fig.update_layout(
            xaxis_title="변동성 (%)",
            yaxis_title="수익률 (%)",
            hovermode='closest'
        )
        st.plotly_chart(fig, width='stretch')  # ✅ warning 해결

        # 최적 포트폴리오
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 최대 Sharpe Ratio 포트폴리오")
            max_sharpe = portfolio.optimize_portfolio(target='max_sharpe')
            st.write(f"수익률: {max_sharpe['return']*100:.2f}%")
            st.write(f"변동성: {max_sharpe['volatility']*100:.2f}%")
            st.write(f"Sharpe Ratio: {max_sharpe['sharpe_ratio']:.2f}")

            weights_df = pd.DataFrame({
                '자산': tickers,
                '가중치': [f"{w:.2%}" for w in max_sharpe['weights']]
            })
            st.table(weights_df)

        with col2:
            st.markdown("#### 최소 변동성 포트폴리오")
            min_vol = portfolio.optimize_portfolio(target='min_variance')
            st.write(f"수익률: {min_vol['return']*100:.2f}%")
            st.write(f"변동성: {min_vol['volatility']*100:.2f}%")
            st.write(f"Sharpe Ratio: {min_vol['sharpe_ratio']:.2f}")

            weights_df = pd.DataFrame({
                '자산': tickers,
                '가중치': [f"{w:.2%}" for w in min_vol['weights']]
            })
            st.table(weights_df)


def render_stress_test(returns, tickers):
    """스트레스 테스트"""
    st.markdown("### 🎓 시나리오 기반 스트레스 테스트")
    st.info("역사적 위기 시나리오를 포트폴리오에 적용하여 리스크를 평가합니다.")

    scenarios = StressScenarios.get_scenarios()

    scenario_names = list(scenarios.keys())
    selected_scenario = st.selectbox(
        "스트레스 시나리오 선택",
        scenario_names,
        format_func=lambda x: scenarios[x]['name']
    )

    scenario = scenarios[selected_scenario]

    # 시나리오 정보 표시
    st.markdown(f"#### {scenario['name']}")
    st.write(scenario['description'])

    # 포트폴리오 구성 (동일 가중)
    weights = np.array([1/len(tickers)] * len(tickers))
    portfolio = PortfolioSimulator(returns, weights)

    # 충격 크기 설정 (간단히 equity_shock 사용)
    shock = scenario.get('equity_shock', -0.3)
    shock_magnitudes = [shock] * len(tickers)

    # 스트레스 테스트 실행
    result = portfolio.stress_test(scenario['name'], shock_magnitudes)

    # 결과 표시
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 포트폴리오 영향")
        st.metric(
            "예상 손실", 
            f"{result['portfolio_shock']*100:.2f}%",
            delta=f"{result['portfolio_shock']*100:.2f}%",
            delta_color="inverse"
        )

        # 금액 기준 (가정: 100만 달러 포트폴리오)
        portfolio_value = 1000000
        loss_amount = portfolio_value * result['portfolio_shock']
        st.metric("금액 기준 손실", f"${loss_amount:,.0f}")

    with col2:
        st.markdown("### 자산별 영향")
        shock_df = pd.DataFrame({
            '자산': tickers,
            '충격 크기': [f"{s*100:.1f}%" for s in shock_magnitudes],
            '포트폴리오 기여': [f"{w * s * 100:.2f}%" for w, s in zip(weights, shock_magnitudes)]
        })
        st.table(shock_df)

    # 여러 시나리오 비교
    if st.button("모든 시나리오 비교"):
        comparison = []
        for scenario_key, scenario_data in scenarios.items():
            shock = scenario_data.get('equity_shock', -0.3)
            shock_mags = [shock] * len(tickers)
            result = portfolio.stress_test(scenario_data['name'], shock_mags)
            comparison.append({
                '시나리오': scenario_data['name'],
                '포트폴리오 손실': f"{result['portfolio_shock']*100:.2f}%"
            })

        comp_df = pd.DataFrame(comparison)
        st.markdown("### 시나리오 비교")
        st.table(comp_df)
