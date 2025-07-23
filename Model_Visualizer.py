import numpy as np
from black_scholes_utils import BlackScholes, create_grid, create_heatmap
from sidebar_control import shared_sidebar
import streamlit as st



# =======================================

# Create markdown box to house the call and put option prices
def styled_box(text, color):
    st.markdown(f"""
    <div style="
        background-color:{color};
        padding:10px;
        border-radius:10px;
        text-align:center;
        font-size:24px;
        font-weight:bold;
        color:black;">
        {text}
    </div>
    """, unsafe_allow_html=True)

# =======================================

# Create sidebar portion shared by both pages and load in saved values
shared_sidebar()

spot_price = st.session_state.spot_price
strike_price= st.session_state.strike_price
time_to_maturity = st.session_state.time_to_maturity
interest_rate = st.session_state.interest_rate
volatility = st.session_state.volatility


# Add all other needed sidebar controls
with st.sidebar:
    
    st.divider()

    st.sidebar.header("Heatmap Parameters")
    
    st.markdown("**Spot Price:**")
    spot_min = st.number_input("Minimum Spot Price", min_value=0.01, value=spot_price * 0.8)
    spot_max = st.number_input("Maximum Spot Price", min_value=0.01, value=spot_price * 1.2)

    st.text("")

    st.markdown("**Volatility:**")
    vol_min, vol_max = st.slider(
        "Volatility Range", 
        min_value=0.01, max_value=1.0, 
        value=(max(0.01, volatility * 0.5), min(1.0, volatility * 1.5))
        )

    if spot_min > spot_max:
        st.error("Minimum Spot Price must be less than Maximum Spot Price.")
        st.stop()
    
    st.text("")

    st.markdown("**Grid Settings:**")
    grid_n = st.sidebar.slider("Grid Density", min_value=5, max_value=25, value=10, step=1)

    st.divider()

    st.markdown("**Misc.**")
    greek_size = st.slider("Metric Font Size", min_value=1, max_value=50, value=30)

    st.markdown(f'<a href="https://www.linkedin.com/in/eli-strayer-93101432a/" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Eli Strayer`</a>', unsafe_allow_html=True) 



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


# Generate needed computations and graphs to input
spot_range = np.linspace(spot_min, spot_max, num=grid_n)
vol_range = np.linspace(vol_min, vol_max, num=grid_n)
call_grid, put_grid = create_grid(spot_range, vol_range, strike_price, time_to_maturity, interest_rate)

x_labels = [f"{num:.2f}" for num in spot_range]
y_labels = [f"{num:.2f}" for num in vol_range]

call_plot = create_heatmap(call_grid, spot_range, vol_range, "Call Prices", grid_n)
put_plot = create_heatmap(put_grid, spot_range, vol_range, "Put Prices", grid_n)    

black_scholes = BlackScholes(spot_price, strike_price, time_to_maturity, interest_rate, volatility)
real_call, real_put = black_scholes.calculate_price()

greeks = black_scholes.greeks()



# Add centered Title
st.markdown(
"""
<h1 style='text-align: center; font-size: 44px; font-weight: bold; color: #fafafa;'>
    Interactive Black-Scholes Model Visualizer
</h1>
""",
unsafe_allow_html=True
)

st.divider()

# Create 5 columns to display the current option parameters
st.subheader("Option Values:")
topcol1, topcol2, topcol3, topcol4, topcol5 = st.columns(5, border=True)

with topcol1:
    st.metric("Spot Price:", f"${spot_price:.2f}")
with topcol2:
    st.metric("Strike Price:", f"${strike_price:.2f}")
with topcol3:
    if time_to_maturity > 1:
        st.metric("Time to Maturity:", f"{time_to_maturity:.2f} Years")
    else:
        st.metric("Time to Maturity:", f"{time_to_maturity:.2f} Year")
with topcol4:
    st.metric("Interest Rate:", f"{interest_rate * 100:.2f}%")
with topcol5:
    st.metric("Volatility:", f"{volatility * 100:.2f}%")


# Create main two center columns to display the heatmaps as well as greeks
col1, col2 = st.columns(2)

# Plot the call heatmap in column 1
with col1: 
    styled_box(f"Call Value: ${real_call:.2f}", "#2ECC71")
    st.text("")
    st.subheader("Call Price Heatmap")
    st.pyplot(call_plot)

    st.subheader("Call Greeks:")
    
    # Create 5 more subcolumns within column 1 to display the greeks below the heatmap
    sub_col1, sub_col2, sub_col3, sub_col4, sub_col5 = st.columns(5)

    with sub_col1:
        st.metric("Delta Δ:", f"{greeks['call_delta']:.3f}")
    with sub_col2:
        st.metric("Gamma γ:", f"{greeks['gamma']:.3f}")
    with sub_col3:
        st.metric("Theta/day θ:", f"{greeks['call_theta_day']:.3f}")
    with sub_col4:
        st.metric("Vega (1%):", f"{greeks['vega_1pct']:.3f}")
    with sub_col5: 
        st.metric("Rho (1%):", f"{greeks['call_rho_1pct']:.3f}")

    # Provide extra information about how the greeks are computed
    with st.popover("Greeks Info", icon=":material/info:"):
        st.markdown(f"Vega shown per +1% of σ.")
        st.markdown(f"Rho shown per +1% rate.")

# Plot the put heatmap in column 2
with col2: 
    styled_box(f"Put Value: ${real_put:.2f}", "#E74C3C")
    st.text("")
    st.subheader("Put Price Heatmap")
    st.pyplot(put_plot)

    st.subheader("Put Greeks:")

    # Same with column 1, create 5 subcolumns to display greeks
    sub_col1, sub_col2, sub_col3, sub_col4, sub_col5 = st.columns(5)
    with sub_col1:
        st.metric("Delta Δ:", f"{greeks['put_delta']:.3f}")
    with sub_col2:
        st.metric("Gamma γ:", f"{greeks['gamma']:.3f}")
    with sub_col3:
        st.metric("Theta/day θ:", f"{greeks['put_theta_day']:.3f}")
    with sub_col4:
        st.metric("Vega (1%):", f"{greeks['vega_1pct']:.3f}")
    with sub_col5: 
        st.metric("Rho (1%):", f"{greeks['put_rho_1pct']:.3f}")
        