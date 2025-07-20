import streamlit as st
from black_scholes_utils import BlackScholes, create_heatmap, pnl_grid
from sidebar_control import shared_sidebar
import numpy as np

def main(): 
    # Set basic page parameters

    st.title("PnL Visualizer")

    option_type = st.sidebar.segmented_control("Option Type", ["Call", "Put"], default="Call")
    shared_sidebar()

    spot_price = st.session_state.spot_price
    strike_price= st.session_state.strike_price
    time_to_maturity = st.session_state.time_to_maturity
    interest_rate = st.session_state.interest_rate
    volatility = st.session_state.volatility


    with st.sidebar:
        st.header("Purchase Price")
        premium = st.number_input("Premium Paid", min_value=0.0, value=10.0)
        contract_mult = st.number_input("Contract Multiplier", min_value=0.0, value=100.0)

        st.divider()

        st.header("Scenario Controls")

        spot_min = st.number_input("Minimum Spot Price", min_value=0.01, value=spot_price * 0.8)
        spot_max = st.number_input("Maximum Spot Price", min_value=0.01, value=spot_price * 1.2)        

        vol_min, vol_max = st.slider(
            "Volatility Range", 
            min_value=0.01, max_value=1.0, 
            value=(max(0.01, volatility * 0.5), min(1.0, volatility * 1.5))
            )
        
        grid_n = st.sidebar.slider("Grid Density", min_value=5, max_value=25, value=10, step=1)

        spot_range = np.linspace(spot_min, spot_max, grid_n)
        vol_range = np.linspace(vol_min, vol_max, grid_n)

        
    if option_type == "Call":
        st.subheader("Call Option PnL Heatmap")

        call_grid = pnl_grid("call", spot_range, vol_range, strike_price, time_to_maturity, interest_rate, premium, contract_mult)
        call_plot = create_heatmap(call_grid, spot_range, vol_range, "Call PnL", grid_n)

        st.pyplot(call_plot)

    
    else:
        st.subheader("Put Option PnL Heatmap")

        put_grid = pnl_grid("put", spot_range, vol_range, strike_price, time_to_maturity, interest_rate, premium, contract_mult)
        put_plot = create_heatmap(put_grid, spot_range, vol_range, "Put PnL", grid_n)

        st.pyplot(put_plot)

main()