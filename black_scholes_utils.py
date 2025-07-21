import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import seaborn as sns
from matplotlib.colors import TwoSlopeNorm
import streamlit as st

# =======================================

# Black scholes equation to calculate prices
class BlackScholes():
    def __init__(self, spot_price, strike_price, time_to_maturity, interest_rate, volatility):
        self.spot_price = spot_price
        self.strike_price = strike_price
        self.time_to_maturity = time_to_maturity
        self.interest_rate = interest_rate
        self.volatility = volatility

    def calculate_price(self):

        S = self.spot_price
        K = self.strike_price
        T = self.time_to_maturity
        r = self.interest_rate

        d1, d2 = self.get_d1d2()

        call_price = norm.cdf(d1) * S - norm.cdf(d2) * K * np.exp(- r * T)

        put_price = K * np.exp(- r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        return call_price, put_price
    

    def get_d1d2(self):
        S = self.spot_price
        K = self.strike_price
        T = self.time_to_maturity
        r = self.interest_rate
        sigma = self.volatility

        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        return d1, d2

    def greeks(self):
        d1, d2 = self.get_d1d2()

        S = self.spot_price
        K = self.strike_price
        T = self.time_to_maturity
        r = self.interest_rate
        sigma = self.volatility

        call_delta = norm.cdf(d1) 
        put_delta = -norm.cdf(-d1)

        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
        vega_raw = S * norm.pdf(d1) * np.sqrt(T)
        vega_1pct = vega_raw / 100.0

        call_theta_yr = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
        put_theta_yr = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
        call_theta_day = call_theta_yr / 365.0
        put_theta_day = put_theta_yr / 365.0

        call_rho = K * T * np.exp(-r * T) * norm.cdf(d2)
        put_rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        call_rho_1pct = call_rho / 100.0
        put_rho_1pct = put_rho / 100.0

        return {
            "call_delta": call_delta,
            "put_delta": put_delta,
            "gamma": gamma,
            "vega": vega_raw,
            "vega_1pct": vega_1pct,
            "call_theta_yr": call_theta_yr,
            "put_theta_yr": put_theta_yr,
            "call_theta_day": call_theta_day,
            "put_theta_day": put_theta_day,
            "call_rho": call_rho,
            "put_rho": put_rho,
            "call_rho_1pct": call_rho_1pct,
            "put_rho_1pct": put_rho_1pct
        }


# =======================================

# Create the grid for the heatmap, plotting the price to its respective spot for the call and put grids and returning it
def create_grid(spot_range, vol_range, strike_price, time_to_maturity, interest_rate):
    call_grid = np.empty((len(vol_range), len(spot_range)))
    put_grid = np.empty((len(vol_range), len(spot_range)))


    for x, vol in enumerate(vol_range):
        for y, spot in enumerate(spot_range):
            bs = BlackScholes(spot, strike_price, time_to_maturity, interest_rate, vol)
            call, put = bs.calculate_price()
            call_grid[x, y] = call
            put_grid[x, y] = put

    return call_grid, put_grid

# =======================================

def draw_sign_boundary(ax, grid, color="black", linewidth=1.5):
    nrows, ncols = grid.shape
    for i in range(nrows):
        for j in range(ncols):
            val = grid[i, j]
            # Check above
            if i > 0 and (val > 0) != (grid[i-1, j] > 0):
                ax.plot([j, j+1], [i, i], color=color, linewidth=linewidth)
            # Check below
            if i < nrows - 1 and (val > 0) != (grid[i+1, j] > 0):
                ax.plot([j, j+1], [i+1, i+1], color=color, linewidth=linewidth)
            # Check left
            if j > 0 and (val > 0) != (grid[i, j-1] > 0):
                ax.plot([j, j], [i, i+1], color=color, linewidth=linewidth)
            # Check Right
            if j < ncols - 1 and (val > 0) != (grid[i, j+1] > 0):
                ax.plot([j+1, j+1], [i, i+1], color=color, linewidth=linewidth)

# =======================================


# Use the previously created call and put price grid to plot a heatmap
def create_heatmap(grid, spot_range, vol_range, title, grid_n):
    
    spot_range = [float(num) for num in spot_range]
    vol_range = [float(num) for num in vol_range]
    
    x_labels = [f"{num:.2f}" for num in spot_range]
    y_labels = [f"{num:.2f}" for num in vol_range]

    max_labels = 10
    step = max(1, len(x_labels) // max_labels)

    vmin = np.min(grid)
    vmax = np.max(grid)
    
    if vmin < 0  and vmax > 0:
        norm = TwoSlopeNorm(vcenter=0, vmin=vmin, vmax=vmax)
    else: 
        norm = plt.Normalize(vmin=vmin, vmax=vmax)

    cmap=plt.get_cmap("RdYlGn")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    font_size = max(6, 14 - grid_n // 2)
    sns.heatmap(grid, annot=True, cmap=cmap, norm=norm, fmt=".2f", annot_kws={"size": font_size}, 
                ax=ax, square=True, xticklabels=False, yticklabels=y_labels)

    draw_sign_boundary(ax, grid, color="black", linewidth=1.5)

    ax.set_xticks(np.arange(0.5, len(x_labels), step))
    rotation = -45 if grid_n > 10 else 0
    ax.set_xticklabels(x_labels[::step], rotation=rotation)
    
    ax.invert_yaxis()
    ax.set_xlabel("Spot Price", fontsize=12)
    ax.set_ylabel("Volatility", fontsize=12)
    ax.set_title(title, fontsize=16)

    return fig
    

# =======================================


def pnl_grid(option_type, spot_range, vol_range, strike_price, time_to_maturity, interest_rate, premium, contract_multiplier=100):
    grid = np.empty((len(vol_range), len(spot_range)), dtype=float)
    for i, vol in enumerate(vol_range):
        for j, spot in enumerate(spot_range):
            bs = BlackScholes(spot, strike_price, time_to_maturity, interest_rate, vol)
            call_price, put_price = bs.calculate_price()

            if option_type == "call":
                grid[i, j] = (call_price - premium) * contract_multiplier
            else:
                grid[i, j] = (put_price - premium) * contract_multiplier
    return grid

# =======================================

def plot_call_payoffs(strike_price, premium, spot_min, spot_max, selected_spot):

    PnL_spot_range = np.linspace(spot_min, spot_max, 100)

   
    pnl_line = np.maximum(0, PnL_spot_range - strike_price) - premium
    fig, ax = plt.subplots()
    ax.plot(PnL_spot_range, pnl_line, label="Call PnL")

    ax.fill_between(PnL_spot_range, pnl_line, 0, where=(pnl_line < 0), color="red", alpha=0.3, interpolate=True)
    ax.fill_between(PnL_spot_range, pnl_line, 0, where=(pnl_line > 0), color="green", alpha=0.3, interpolate=True)

    ax.grid(True, linestyle='--', alpha=0.5)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')
    
    ax.axvline(selected_spot, color="blue", linewidth=1, linestyle=":", label=f"Spot = {selected_spot:.2f}")
    
    breakeven = strike_price + premium
    ax.axvline(breakeven, color="red", linewidth=1, linestyle="--", label=f"Breakeven = {breakeven:.2f}")
    ax.set_xlabel("Spot Price")
    ax.set_ylabel("PnL")
    ax.set_title("Call Option Payoff")
    
    ax.legend()
    fig.tight_layout()

    return fig

# =============================================

def plot_put_payoffs(strike_price, premium, spot_min, spot_max, selected_spot):

    PnL_spot_range = np.linspace(spot_min, spot_max, 100)

   
    pnl_line = np.maximum(0, strike_price - PnL_spot_range) - premium
    fig, ax = plt.subplots()
    ax.plot(PnL_spot_range, pnl_line, label="Put PnL")

    ax.fill_between(PnL_spot_range, pnl_line, 0, where=(pnl_line < 0), color="red", alpha=0.3, interpolate=True)
    ax.fill_between(PnL_spot_range, pnl_line, 0, where=(pnl_line > 0), color="green", alpha=0.3, interpolate=True)

    ax.grid(True, linestyle='--', alpha=0.5)

    ax.axhline(0, color='black', linewidth=1, linestyle='--')

    ax.axvline(selected_spot, color="blue", linewidth=1, linestyle=":", label=f"Spot = {selected_spot:.2f}")
    
    breakeven = strike_price - premium
    ax.axvline(breakeven, color="red", linewidth=1, linestyle="--", label=f"Breakeven = {breakeven:.2f}")
    ax.set_xlabel("Spot Price")
    ax.set_ylabel("PnL")
    ax.set_title("Put Option Payoff")
    
    ax.legend()
    fig.tight_layout()

    return fig

