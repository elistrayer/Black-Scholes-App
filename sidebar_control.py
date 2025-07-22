import streamlit as st

# Create the sidebar shared by both pages and save the values inputted to allow seamless transition between pages
def shared_sidebar():
    st.sidebar.header("Option Parameters")

    st.session_state.spot_price = st.sidebar.number_input(
        "Spot Price",
        value=st.session_state.get("spot_price", 100.0),
        step=0.1
    )

    st.session_state.strike_price = st.sidebar.number_input(
        "Strike Price",
        value=st.session_state.get("strike_price", 100.0),
        step=0.1
    )

    st.session_state.time_to_maturity = st.sidebar.number_input(
        "Time to Maturity",
        value=st.session_state.get("time_to_maturity", 1.0),
        step=0.1
    )

    st.session_state.interest_rate = st.sidebar.number_input(
        "Interest Rate",
        value=st.session_state.get("interest_rate", 0.05),
        step=0.01
    )

    st.session_state.volatility = st.sidebar.number_input(
        "Volatility",
        value=st.session_state.get("volatility", 0.20),
        step=0.01
    )