
def render_bond_yield_curve():
    """채권 & 수익률 곡선 시뮬레이션"""
    st.header("채권 가격 & 수익률 곡선 분석")

    tab_a, tab_b = st.tabs(["채권 가격 계산", "수익률 곡선 시뮬레이션"])

    with tab_a:
        col1, col2 = st.columns(2)

        with col1:
            face_value = st.number_input("액면가", value=1000.0)
            coupon_rate = st.slider("표면이율 (%)", 0.0, 10.0, 5.0, 0.1) / 100
            ytm = st.slider("만기수익률 (%)", 0.0, 15.0, 6.0, 0.1) / 100
            years = st.number_input("만기 (년)", value=5, min_value=1, max_value=30)
            frequency = st.selectbox("이자 지급 횟수", [1, 2, 4], index=1)

        periods = years * frequency
        price = BondPricer.price_bond(face_value, coupon_rate, ytm, periods, frequency)
        duration = BondPricer.duration(face_value, coupon_rate, ytm, periods, frequency)

        with col2:
            st.markdown("### 계산 결과")
            st.metric("채권 가격", f"${price:.2f}")
            st.metric("듀레이션", f"{duration:.2f}년")
            st.metric("할인/할증", f"${price - face_value:+.2f}")

        # YTM에 따른 가격 변화
        st.markdown("### 만기수익률에 따른 가격 변화")
        ytm_range = np.linspace(max(0.001, ytm - 0.05), ytm + 0.05, 50)
        prices = [BondPricer.price_bond(face_value, coupon_rate, y, periods, frequency) for y in ytm_range]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ytm_range*100, y=prices, mode='lines', name='채권 가격'))
        fig.add_vline(x=ytm*100, line_dash="dash", line_color="red", annotation_text="현재 YTM")
        fig.update_layout(
            xaxis_title="만기수익률 (%)",
            yaxis_title="채권 가격 ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, width='stretch')  # ✅ warning 해결

    with tab_b:
        st.markdown("### 🎓 수익률 곡선 변화 시뮬레이션")
        st.info("수익률 곡선의 Parallel Shift, Steepening, Flattening 효과를 시뮬레이션합니다.")

        fetcher = DataFetcher()
        base_yields = fetcher.get_treasury_yields()

        col1, col2 = st.columns([1, 2])

        with col1:
            shift_type = st.radio(
                "수익률 곡선 변화 유형",
                ['parallel', 'steepening', 'flattening']
            )

            magnitude_bp = st.slider("변화 크기 (bp)", -200, 200, 100, 10)
            magnitude = magnitude_bp / 10000  # bp to decimal

            st.markdown(f"""
            **선택한 시나리오:**
            - {shift_type.upper()}
            - {magnitude_bp:+d} basis points
            """)

        with col2:
            # 기본 수익률 곡선
            shifted_yields = BondPricer.simulate_yield_curve_shift(
                base_yields, shift_type, magnitude
            )

            fig = go.Figure()

            # 기본 곡선
            fig.add_trace(go.Scatter(
                x=list(base_yields.index),
                y=base_yields.values,
                mode='lines+markers',
                name='기본 곡선',
                line=dict(color='blue', width=2)
            ))

            # 변화된 곡선
            fig.add_trace(go.Scatter(
                x=list(shifted_yields.index),
                y=shifted_yields.values,
                mode='lines+markers',
                name=f'{shift_type.capitalize()} ({magnitude_bp:+d}bp)',
                line=dict(color='red', width=2, dash='dash')
            ))

            fig.update_layout(
                title="수익률 곡선 변화",
                xaxis_title="만기",
                yaxis_title="수익률 (%)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, width='stretch')  # ✅ warning 해결

            # 채권 가격 영향 분석
            st.markdown("### 채권 포트폴리오 영향")

            maturities = [2, 5, 10, 30]
            price_changes = []

            for mat in maturities:
                base_ytm = base_yields.get(f'{mat}Y', 4.0) / 100
                shifted_ytm = shifted_yields.get(f'{mat}Y', 4.0) / 100

                base_price = BondPricer.price_bond(1000, 0.05, base_ytm, mat*2, 2)
                shifted_price = BondPricer.price_bond(1000, 0.05, shifted_ytm, mat*2, 2)

                price_change = ((shifted_price - base_price) / base_price) * 100
                price_changes.append(price_change)

            impact_df = pd.DataFrame({
                '만기': [f'{m}년' for m in maturities],
                '가격 변화 (%)': [f'{pc:+.2f}%' for pc in price_changes]
            })

            st.table(impact_df)


def render_options_strategies():
    """옵션 & 전략 시뮬레이션"""
    st.header("옵션 가격 계산 & 전략 시뮬레이터")

    tab_a, tab_b = st.tabs(["기본 옵션", "옵션 전략 빌더"])

    with tab_a:
        col1, col2 = st.columns(2)

        with col1:
            S = st.number_input("기초자산 가격", value=100.0)
            K = st.number_input("행사가격", value=100.0)
            T = st.slider("만기까지 기간 (년)", 0.1, 3.0, 1.0, 0.1)
            r = st.slider("무위험이자율 (%)", 0.0, 10.0, 2.0, 0.1) / 100
            sigma = st.slider("변동성 (연율) (%)", 5.0, 100.0, 30.0, 1.0) / 100
            option_type = st.radio("옵션 유형", ['call', 'put'])

        option_price = OptionPricer.black_scholes(S, K, T, r, sigma, option_type)
        greeks = OptionPricer.greeks(S, K, T, r, sigma, option_type)

        with col2:
            st.markdown("### 계산 결과")
            st.metric("옵션 가격", f"${option_price:.4f}")

            st.markdown("### Greeks")
            col_a, col_b = st.columns(2)
            col_a.metric("Delta", f"{greeks['Delta']:.4f}")
            col_b.metric("Gamma", f"{greeks['Gamma']:.4f}")
            col_a.metric("Vega", f"{greeks['Vega']:.4f}")
            col_b.metric("Theta", f"{greeks['Theta']:.4f}")
            st.metric("Rho", f"{greeks['Rho']:.4f}")

        # Payoff Diagram
        st.markdown("### 📊 페이오프 다이어그램")
        S_range = np.linspace(S * 0.5, S * 1.5, 100)
        payoff = OptionPricer.payoff_diagram(S_range, K, option_type, option_price, 'long')

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=S_range,
            y=payoff,
            mode='lines',
            name=f'Long {option_type.capitalize()}',
            line=dict(color='blue', width=2)
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        fig.add_vline(x=K, line_dash="dash", line_color="red", annotation_text="행사가격")
        fig.update_layout(
            xaxis_title="기초자산 가격 ($)",
            yaxis_title="손익 ($)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, width='stretch')  # ✅ warning 해결

    with tab_b:
        st.markdown("### 🎓 옵션 전략 빌더")

        strategy = st.selectbox(
            "전략 선택",
            ["커스텀", "Covered Call", "Protective Put", "Straddle", "Strangle", "Bull Call Spread"]
        )

        S_current = st.number_input("현재 기초자산 가격", value=100.0, key='strategy_S')

        if strategy == "Covered Call":
            # Long Stock + Short Call
            legs = [
                {'type': 'call', 'K': S_current * 1.1, 'premium': 5.0, 'position': 'short'}
            ]
            st.info("전략: 주식 보유 + Call 옵션 매도. 제한된 상승 이익, 프리미엄 수익.")

        elif strategy == "Protective Put":
            # Long Stock + Long Put
            legs = [
                {'type': 'put', 'K': S_current * 0.9, 'premium': 3.0, 'position': 'long'}
            ]
            st.info("전략: 주식 보유 + Put 옵션 매수. 하방 리스크 제한.")

        elif strategy == "Straddle":
            # Long Call + Long Put (동일 행사가)
            legs = [
                {'type': 'call', 'K': S_current, 'premium': 5.0, 'position': 'long'},
                {'type': 'put', 'K': S_current, 'premium': 5.0, 'position': 'long'}
            ]
            st.info("전략: Call + Put 동시 매수. 큰 변동성 예상 시 사용.")

        elif strategy == "Strangle":
            # Long Call + Long Put (다른 행사가)
            legs = [
                {'type': 'call', 'K': S_current * 1.1, 'premium': 3.0, 'position': 'long'},
                {'type': 'put', 'K': S_current * 0.9, 'premium': 3.0, 'position': 'long'}
            ]
            st.info("전략: OTM Call + OTM Put 매수. Straddle보다 저렴, 더 큰 변동 필요.")

        elif strategy == "Bull Call Spread":
            # Long Call (낮은 K) + Short Call (높은 K)
            legs = [
                {'type': 'call', 'K': S_current, 'premium': 5.0, 'position': 'long'},
                {'type': 'call', 'K': S_current * 1.1, 'premium': 2.0, 'position': 'short'}
            ]
            st.info("전략: ITM Call 매수 + OTM Call 매도. 제한된 손익, 비용 감소.")
        else:
            # 커스텀
            legs = []
            st.warning("커스텀 전략은 아래에서 직접 구성하세요.")

        if strategy != "커스텀" and legs:
            S_range = np.linspace(S_current * 0.6, S_current * 1.4, 100)
            total_payoff = OptionPricer.strategy_payoff(S_range, legs)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=S_range,
                y=total_payoff,
                mode='lines',
                name=strategy,
                line=dict(color='purple', width=3)
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.add_vline(x=S_current, line_dash="dash", line_color="blue", annotation_text="현재가")
            fig.update_layout(
                title=f"{strategy} 페이오프 다이어그램",
                xaxis_title="기초자산 가격 ($)",
                yaxis_title="손익 ($)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, width='stretch')  # ✅ warning 해결


def render_hedge_swap():
    """헤지 & 금리 스왑 시뮬레이션"""
    st.header("헤지 & 금리 스왑 시뮬레이터")

    tab_a, tab_b = st.tabs(["선물 헤지", "금리 스왑"])

    with tab_a:
        st.markdown("### 🎓 주식 포지션 선물 헤지 시뮬레이션")

        col1, col2 = st.columns(2)

        with col1:
            stock_value = st.number_input("주식 포지션 가치 ($)", value=1000000.0, step=10000.0)
            futures_price = st.number_input("선물 가격 ($)", value=250.0)
            hedge_ratio = st.slider("헤지 비율 (%)", 0, 100, 100, 10)

            # 계약 수 계산
            contracts_needed = -(stock_value / futures_price) * (hedge_ratio / 100)
            st.info(f"필요 선물 계약 수: {contracts_needed:.0f}개 (매도)")

        with col2:
            st.markdown("### 시나리오 분석")
            scenarios = st.multiselect(
                "시장 시나리오 선택",
                ["-30%", "-20%", "-10%", "0%", "+10%", "+20%", "+30%"],
                default=["-20%", "0%", "+20%"]
            )

        if scenarios:
            results = []
            for scenario in scenarios:
                change = float(scenario.replace('%', '')) / 100
                result = HedgeSimulator.stock_futures_hedge(
                    stock_value, futures_price, contracts_needed, change
                )
                result['scenario'] = scenario
                results.append(result)

            df = pd.DataFrame(results)
            df = df[['scenario', 'stock_pl', 'futures_pl', 'total_pl', 'hedge_efficiency']]
            df.columns = ['시나리오', '주식 손익 ($)', '선물 손익 ($)', '총 손익 ($)', '헤지 효율 (%)']
            df['헤지 효율 (%)'] = df['헤지 효율 (%)'].apply(lambda x: f'{x*100:.1f}%')

            st.dataframe(df, width=800)

            # 시각화
            fig = go.Figure()
            scenarios_num = [float(s.replace('%', '')) for s in scenarios]
            stock_pls = [r['stock_pl'] for r in results]
            total_pls = [r['total_pl'] for r in results]

            fig.add_trace(go.Scatter(
                x=scenarios_num, y=stock_pls, mode='lines+markers',
                name='헤지 없음', line=dict(color='red', width=2)
            ))
            fig.add_trace(go.Scatter(
                x=scenarios_num, y=total_pls, mode='lines+markers',
                name='헤지 있음', line=dict(color='green', width=2)
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(
                title="헤지 효과",
                xaxis_title="시장 변동 (%)",
                yaxis_title="손익 ($)",
                hovermode='x unified'
            )
            st.plotly_chart(fig, width='stretch')  # ✅ warning 해결

    with tab_b:
        st.markdown("### 🎓 금리 스왑 (IRS) 시뮬레이션")
        st.info("변동금리 대출을 받은 기업이 IRS로 고정금리로 전환하는 시나리오")

        col1, col2 = st.columns(2)

        with col1:
            notional = st.number_input("명목원금 ($)", value=10000000.0, step=100000.0)
            fixed_rate = st.slider("고정금리 (%)", 1.0, 10.0, 4.0, 0.1) / 100
            periods = st.number_input("지급 횟수", value=10, min_value=1, max_value=40)

            st.markdown("### 변동금리 시나리오")
            scenario = st.radio(
                "금리 추세",
                ["상승", "하락", "변동"]
            )

        # 변동금리 시나리오 생성
        base_rate = fixed_rate
        if scenario == "상승":
            floating_rates = [base_rate + (i * 0.002) for i in range(periods)]
        elif scenario == "하락":
            floating_rates = [base_rate - (i * 0.002) for i in range(periods)]
        else:
            np.random.seed(42)
            floating_rates = [base_rate + np.random.uniform(-0.01, 0.01) for i in range(periods)]

        # IRS 현금흐름 계산
        cashflows = InterestRateSwap.calculate_cashflows(
            notional, fixed_rate, floating_rates, periods
        )

        with col2:
            st.markdown("### 현금흐름 분석")
            total_fixed = cashflows['Fixed_Payment'].sum()
            total_floating = cashflows['Floating_Payment'].sum()
            total_net = cashflows['Net_Payment'].sum()

            st.metric("총 고정금리 지급", f"${total_fixed:,.0f}")
            st.metric("총 변동금리 지급", f"${total_floating:,.0f}")
            st.metric("순 현금흐름", f"${total_net:+,.0f}")

            if total_net > 0:
                st.success(f"IRS를 통해 ${abs(total_net):,.0f} 추가 지급")
            else:
                st.success(f"IRS를 통해 ${abs(total_net):,.0f} 절감!")

        # 현금흐름 차트
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=cashflows['Period'], y=cashflows['Fixed_Payment'],
            name='고정금리 지급', marker_color='blue'
        ))
        fig.add_trace(go.Bar(
            x=cashflows['Period'], y=cashflows['Floating_Payment'],
            name='변동금리 지급', marker_color='orange'
        ))
        fig.update_layout(
            title="IRS 현금흐름",
            xaxis_title="기간",
            yaxis_title="금액 ($)",
            barmode='group'
        )
        st.plotly_chart(fig, width='stretch')  # ✅ warning 해결
