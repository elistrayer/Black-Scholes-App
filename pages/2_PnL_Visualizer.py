import streamlit as st
from black_scholes_utils import BlackScholes, create_heatmap, pnl_grid, plot_call_payoffs, plot_put_payoffs, time_loss, plot_time_loss
from sidebar_control import shared_sidebar
import numpy as np
import matplotlib.pyplot as plt





# Title
st.markdown(
"""
<h1 style='text-align: center; font-size: 44px; font-weight: bold; color: #fafafa;'>
    PnL Dashboard
</h1>
""",
unsafe_allow_html=True
)


st.divider()

# Start sidebar setup with option type selection
option_type = st.sidebar.segmented_control("Option Type", ["Call", "Put"], default="Call")
if not option_type:
    option_type = "Call"

# Use function to setup the portion of sidebar shared by both pages
shared_sidebar()

# Load in the values so they remain constant between pages
spot_price = st.session_state.spot_price
strike_price= st.session_state.strike_price
time_to_maturity = st.session_state.time_to_maturity
interest_rate = st.session_state.interest_rate
volatility = st.session_state.volatility


# Add all other needed sidebar controls
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

    st.divider()

    st.markdown("**Misc.**")
    greek_size = st.slider("Metric Font Size", min_value=1, max_value=50, value=30)

# Allow user to change the size of streamlit metrics
st.markdown(
    f"""
    <style>
    [data-testid="stMetricValue"] > div {{
        font-size: {greek_size}px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
    ) 


# Set up first pair of columns
col1, col2 = st.columns(2)

# Start with column 2 as column 1 has variables that depend on it
with col2:
    st.subheader("Key Metrics")

    # Change font size of slider title
    st.markdown(
        """
        <style>
        /* Target the slider label */
        div[data-testid="stSlider"] label p {
            font-size: 20px !important;
            font-weight: 560 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
        )

    # Create a slider that lets users select a spot price
    selected_spot = st.slider("Select Spot Price", spot_min, spot_max, (spot_min + spot_max) / 2)
    
    # Caclulate greeks, breakeven, and PnL using selected spot Pnl
    black_scholes = BlackScholes(selected_spot, strike_price, time_to_maturity, interest_rate, volatility)
    greeks = black_scholes.greeks()

    if option_type == "Call":
        breakeven = strike_price + premium
        current_pnl = np.maximum(0, selected_spot - strike_price) - premium

    if option_type == "Put":
        breakeven = strike_price - premium
        current_pnl = np.maximum(0, strike_price - selected_spot) - premium

    # Set up three subcolumns for first three metrics
    col21, col22, col23 = st.columns(3, border=True)
    col21.metric("Breakeven", f"${breakeven:.2f}")
    col22.metric("Max Loss", f"-${premium:.2f}")
    with col23:
        if current_pnl < 0:
            current_pnl = abs(current_pnl)
            st.metric("PnL at Selected Spot", f"-${current_pnl:.2f}")
        else:
            st.metric("PnL at Selected Spot", f"${current_pnl:.2f}")

    
    st.text("")
    
    # Set up 5 more subcolumns for 5 greeks
    st.markdown("##### Greeks at Selected Spot")
    col31, col32, col33, col34, col35 = st.columns(5)

    with col31:
        if option_type == "Call":
            st.metric("Delta Δ:", f"{greeks['call_delta']:.3f}")
        else:
            st.metric("Delta Δ:", f"{greeks['put_delta']:.3f}")

    with col32:
        if option_type == "Call":
            st.metric("Theta/day θ:", f"{greeks['call_theta_day']:.3f}")
        else:
            st.metric("Theta/day θ:", f"{greeks['put_theta_day']:.3f}")
    
    with col33: 
        if option_type == "Call":
            st.metric("Rho (1%):", f"{greeks['call_rho_1pct']:.3f}")
        else: 
            st.metric("Rho (1%):", f"{greeks['put_rho_1pct']:.3f}")
    
    with col34:
        st.metric("Gamma γ:", f"{greeks['gamma']:.3f}")
    
    
    with col35:
        st.metric("Vega (1%):", f"{greeks['vega_1pct']:.3f}")




# Add PnL chart to column 1
with col1:
    if option_type == "Call":
        st.subheader("Call Option PnL Chart")
        fig = plot_call_payoffs(strike_price, premium, spot_min, spot_max, selected_spot)
        st.pyplot(fig)
        
    else:
        st.subheader("Put Option PnL Chart")
        fig = plot_put_payoffs(strike_price, premium, spot_min, spot_max, selected_spot)
        st.pyplot(fig)
        

st.text("")
st.text("")


# Create two more columns identical to the two above (this allows the next two charts to always be level)
sub_col1, sub_col2 = st.columns(2)

# Create the time decay chart in column 1
with sub_col1:
    st.subheader("Time Decay Chart")
    time_steps, prices = time_loss(spot_price, strike_price, time_to_maturity, interest_rate, volatility, option_type)
    plot_time_loss(time_steps, prices, premium)

# Create the PnL heatmap in column 2
with sub_col2:
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

