"""
VectorBT Strategy Backtest Template

This is a complete, production-ready template for developing and testing
quantitative trading strategies using vectorbt.

INSTRUCTIONS:
1. Modify the strategy parameters in the CONFIGURATION section
2. Implement your signal generation logic in generate_signals()
3. Run the backtest and analyze results
4. If criteria are met, submit to Alpha Vault using submit_alpha_telemetry()

REQUIREMENTS:
- Python 3.8+
- vectorbt-pro or vectorbt
- pandas, numpy

INSTALL:
pip install vectorbt pandas numpy yfinance

Author: Senior Quantitative Researcher
Template Version: 1.0
"""

import numpy as np
import pandas as pd
import vectorbt as vbt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Strategy Metadata
STRATEGY_NAME = "Mean_Reversion_ZScore"
HYPOTHESIS = """
Price tends to revert to its mean after extreme deviations.
When price moves more than 1.5 standard deviations below its 20-day mean,
it tends to bounce back, presenting a buying opportunity.
"""

# Strategy Parameters
PARAMS = {
    'lookback_period': 20,      # Window for calculating mean and std
    'entry_threshold': 1.5,     # Z-score threshold for entry
    'exit_threshold': 0.5,      # Z-score threshold for exit
    'position_size': 1.0,       # Fraction of capital per trade (1.0 = 100%)
    'stop_loss_pct': 0.05,      # Stop loss as fraction (5%)
    'take_profit_pct': 0.10,    # Take profit as fraction (10%)
}

# Backtest Configuration
BACKTEST_CONFIG = {
    'symbol': 'BTC-USD',        # Trading symbol
    'start_date': '2020-01-01', # Backtest start
    'end_date': '2023-12-31',   # Backtest end
    'initial_capital': 100000,  # Starting capital ($)
    'commission': 0.001,        # Commission per trade (0.1%)
    'slippage': 0.0005,         # Slippage estimate (0.05%)
    'freq': '1D',               # Data frequency
}

# Alpha Vault Criteria (from config.py)
ALPHA_VAULT_CRITERIA = {
    'min_sharpe_ratio': 1.5,
    'min_trades': 100,
    'max_drawdown': -0.30,      # -30%
    'min_win_rate': 0.45,       # 45%
}

# ============================================================================
# DATA LOADING
# ============================================================================

def load_data(symbol=None, start=None, end=None, freq='1D'):
    """
    Load historical price data using vectorbt's Yahoo Finance integration.

    Parameters:
        symbol (str): Trading symbol (e.g., 'BTC-USD', 'AAPL')
        start (str): Start date in 'YYYY-MM-DD' format
        end (str): End date in 'YYYY-MM-DD' format
        freq (str): Data frequency ('1D', '1H', etc.)

    Returns:
        pd.Series: Close prices with datetime index
    """
    symbol = symbol or BACKTEST_CONFIG['symbol']
    start = start or BACKTEST_CONFIG['start_date']
    end = end or BACKTEST_CONFIG['end_date']

    print(f"Loading data for {symbol} from {start} to {end}...")

    try:
        # Download data using vectorbt
        data = vbt.YFData.download(
            symbol,
            start=start,
            end=end,
            missing_index='drop'
        )

        # Extract close prices
        close_prices = data.get('Close')

        # Validate data
        if close_prices is None or len(close_prices) == 0:
            raise ValueError("No data retrieved")

        # Remove NaN values
        close_prices = close_prices.dropna()

        print(f"✓ Loaded {len(close_prices)} data points")
        print(f"  Date range: {close_prices.index[0]} to {close_prices.index[-1]}")
        print(f"  Price range: ${close_prices.min():.2f} to ${close_prices.max():.2f}")

        return close_prices

    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return None


def load_multiple_symbols(symbols, start=None, end=None):
    """
    Load data for multiple symbols (for pairs trading or portfolio strategies).

    Parameters:
        symbols (list): List of symbol strings
        start (str): Start date
        end (str): End date

    Returns:
        pd.DataFrame: Close prices with symbols as columns
    """
    start = start or BACKTEST_CONFIG['start_date']
    end = end or BACKTEST_CONFIG['end_date']

    print(f"Loading data for {len(symbols)} symbols...")

    try:
        data = vbt.YFData.download(
            symbols,
            start=start,
            end=end,
            missing_index='drop'
        )

        close_prices = data.get('Close')

        # Handle single vs multiple columns
        if isinstance(close_prices, pd.Series):
            close_prices = close_prices.to_frame()

        # Drop NaN values
        close_prices = close_prices.dropna()

        print(f"✓ Loaded {len(close_prices)} data points for {close_prices.shape[1]} symbols")

        return close_prices

    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return None

# ============================================================================
# TECHNICAL INDICATORS
# ============================================================================

def calculate_z_score(prices, window=20):
    """
    Calculate z-score (standardized deviation from mean).

    Z-score = (Price - Mean) / StdDev

    Parameters:
        prices (pd.Series): Price series
        window (int): Rolling window size

    Returns:
        pd.Series: Z-score values
    """
    rolling_mean = prices.rolling(window=window).mean()
    rolling_std = prices.rolling(window=window).std()
    z_score = (prices - rolling_mean) / rolling_std
    return z_score


def calculate_rsi(prices, window=14):
    """
    Calculate Relative Strength Index (RSI).

    Parameters:
        prices (pd.Series): Price series
        window (int): RSI period (default 14)

    Returns:
        pd.Series: RSI values (0-100)
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_bollinger_bands(prices, window=20, num_std=2):
    """
    Calculate Bollinger Bands.

    Parameters:
        prices (pd.Series): Price series
        window (int): Moving average period
        num_std (float): Number of standard deviations

    Returns:
        tuple: (upper_band, middle_band, lower_band)
    """
    middle_band = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)

    return upper_band, middle_band, lower_band


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Parameters:
        prices (pd.Series): Price series
        fast (int): Fast EMA period
        slow (int): Slow EMA period
        signal (int): Signal line period

    Returns:
        tuple: (macd_line, signal_line, histogram)
    """
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_atr(high, low, close, window=14):
    """
    Calculate Average True Range (ATR) for volatility.

    Parameters:
        high (pd.Series): High prices
        low (pd.Series): Low prices
        close (pd.Series): Close prices
        window (int): ATR period

    Returns:
        pd.Series: ATR values
    """
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=window).mean()
    return atr

# ============================================================================
# SIGNAL GENERATION
# ============================================================================

def generate_signals(prices, params=None):
    """
    Generate trading entry and exit signals.

    THIS IS WHERE YOU IMPLEMENT YOUR STRATEGY LOGIC.

    The example below implements a mean-reversion strategy based on z-score:
    - Enter LONG when price drops below -entry_threshold standard deviations
    - Exit when price reverts above -exit_threshold standard deviations

    Parameters:
        prices (pd.Series): Price data
        params (dict): Strategy parameters

    Returns:
        tuple: (entries, exits) - Boolean pandas Series
    """
    params = params or PARAMS

    # Extract parameters
    lookback = params['lookback_period']
    entry_z = params['entry_threshold']
    exit_z = params['exit_threshold']

    # Calculate z-score
    z_score = calculate_z_score(prices, window=lookback)

    # Generate signals
    # LONG ENTRIES: Price is oversold (z-score very negative)
    entries = z_score < -entry_z

    # LONG EXITS: Price has reverted toward mean
    exits = z_score > -exit_z

    # Remove NaN values (from initial rolling window)
    entries = entries.fillna(False)
    exits = exits.fillna(False)

    return entries, exits


def generate_signals_momentum(prices, params=None):
    """
    Example momentum strategy (alternative implementation).

    Uses moving average crossover:
    - Enter when fast MA crosses above slow MA
    - Exit when fast MA crosses below slow MA
    """
    # Calculate moving averages
    fast_ma = prices.rolling(window=10).mean()
    slow_ma = prices.rolling(window=30).mean()

    # Crossover signals
    entries = (fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))
    exits = (fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))

    entries = entries.fillna(False)
    exits = exits.fillna(False)

    return entries, exits


def generate_signals_rsi(prices, params=None):
    """
    Example RSI-based strategy (alternative implementation).

    - Enter when RSI < 30 (oversold)
    - Exit when RSI > 70 (overbought)
    """
    rsi = calculate_rsi(prices, window=14)

    entries = rsi < 30
    exits = rsi > 70

    entries = entries.fillna(False)
    exits = exits.fillna(False)

    return entries, exits

# ============================================================================
# BACKTESTING
# ============================================================================

def run_backtest(prices, entries, exits, config=None):
    """
    Execute backtest using vectorbt Portfolio simulator.

    Parameters:
        prices (pd.Series): Price data
        entries (pd.Series): Entry signals (boolean)
        exits (pd.Series): Exit signals (boolean)
        config (dict): Backtest configuration

    Returns:
        vbt.Portfolio: Portfolio object with complete backtest results
    """
    config = config or BACKTEST_CONFIG

    # Create portfolio from signals
    portfolio = vbt.Portfolio.from_signals(
        close=prices,
        entries=entries,
        exits=exits,
        init_cash=config['initial_capital'],
        fees=config['commission'],
        slippage=config['slippage'],
        freq=config['freq'],
        # Additional optional parameters:
        # size=position_size,  # For fixed position sizing
        # size_type='percent',  # or 'amount', 'value'
        # accumulate=False,  # Don't accumulate positions
    )

    return portfolio


def run_backtest_with_stops(prices, entries, exits, config=None, params=None):
    """
    Execute backtest with stop-loss and take-profit levels.

    Parameters:
        prices (pd.Series): Price data
        entries (pd.Series): Entry signals
        exits (pd.Series): Exit signals
        config (dict): Backtest configuration
        params (dict): Strategy parameters

    Returns:
        vbt.Portfolio: Portfolio with stop-loss/take-profit applied
    """
    config = config or BACKTEST_CONFIG
    params = params or PARAMS

    # Extract stop levels
    sl_pct = params.get('stop_loss_pct', 0.05)
    tp_pct = params.get('take_profit_pct', 0.10)

    # Create portfolio with stops
    portfolio = vbt.Portfolio.from_signals(
        close=prices,
        entries=entries,
        exits=exits,
        init_cash=config['initial_capital'],
        fees=config['commission'],
        slippage=config['slippage'],
        freq=config['freq'],
        sl_stop=sl_pct,      # Stop loss
        tp_stop=tp_pct,      # Take profit
    )

    return portfolio

# ============================================================================
# PERFORMANCE METRICS
# ============================================================================

def calculate_metrics(portfolio):
    """
    Calculate comprehensive performance metrics for Alpha Vault submission.

    Parameters:
        portfolio (vbt.Portfolio): Backtest results

    Returns:
        dict: Performance metrics matching Alpha Vault schema
    """
    # Return metrics
    total_return = portfolio.total_return()
    annual_return = portfolio.annualized_return()

    # Risk-adjusted metrics
    sharpe_ratio = portfolio.sharpe_ratio()
    sortino_ratio = portfolio.sortino_ratio()
    calmar_ratio = portfolio.calmar_ratio()

    # Drawdown metrics
    max_drawdown = portfolio.max_drawdown()
    avg_drawdown = portfolio.drawdowns.avg_drawdown()
    max_dd_duration = portfolio.drawdowns.max_duration()

    # Trade statistics
    trades = portfolio.trades.records_readable
    total_trades = len(trades)

    if total_trades > 0:
        winning_trades = trades[trades['PnL'] > 0]
        losing_trades = trades[trades['PnL'] < 0]

        win_rate = len(winning_trades) / total_trades

        avg_win = winning_trades['PnL'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['PnL'].mean()) if len(losing_trades) > 0 else 1

        profit_factor = avg_win / avg_loss if avg_loss > 0 else 0

        # Trade duration in days
        avg_duration = trades['Duration'].mean() / pd.Timedelta(days=1)
        max_duration = trades['Duration'].max() / pd.Timedelta(days=1)

        # Expectancy
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    else:
        win_rate = 0
        avg_win = 0
        avg_loss = 0
        profit_factor = 0
        avg_duration = 0
        max_duration = 0
        expectancy = 0

    # Compile metrics dictionary
    metrics = {
        # Core performance
        'total_return': float(total_return),
        'annual_return': float(annual_return),

        # Risk-adjusted returns
        'sharpe_ratio': float(sharpe_ratio),
        'sortino_ratio': float(sortino_ratio),
        'calmar_ratio': float(calmar_ratio),

        # Drawdown
        'max_drawdown': float(max_drawdown),
        'avg_drawdown': float(avg_drawdown),
        'max_dd_duration_days': float(max_dd_duration / pd.Timedelta(days=1)) if max_dd_duration else 0,

        # Trade statistics
        'total_trades': int(total_trades),
        'win_rate': float(win_rate),
        'profit_factor': float(profit_factor),
        'avg_win': float(avg_win),
        'avg_loss': float(avg_loss),
        'expectancy': float(expectancy),

        # Trade duration
        'avg_trade_duration_days': float(avg_duration),
        'max_trade_duration_days': float(max_duration),
    }

    return metrics


def validate_alpha_vault_criteria(metrics, criteria=None):
    """
    Check if strategy meets Alpha Vault submission criteria.

    Parameters:
        metrics (dict): Performance metrics
        criteria (dict): Alpha Vault criteria thresholds

    Returns:
        tuple: (passes: bool, report: dict)
    """
    criteria = criteria or ALPHA_VAULT_CRITERIA

    checks = {
        'sharpe_ratio': metrics['sharpe_ratio'] > criteria['min_sharpe_ratio'],
        'trade_count': metrics['total_trades'] > criteria['min_trades'],
        'max_drawdown': metrics['max_drawdown'] > criteria['max_drawdown'],
        'win_rate': metrics['win_rate'] > criteria['min_win_rate'],
    }

    passes = all(checks.values())

    report = {
        'passes': passes,
        'checks': checks,
        'metrics': {
            'sharpe_ratio': metrics['sharpe_ratio'],
            'total_trades': metrics['total_trades'],
            'max_drawdown': metrics['max_drawdown'],
            'win_rate': metrics['win_rate'],
        },
        'criteria': criteria
    }

    return passes, report

# ============================================================================
# REPORTING
# ============================================================================

def print_performance_report(metrics, validation_report=None):
    """
    Print formatted performance report to console.

    Parameters:
        metrics (dict): Performance metrics
        validation_report (dict): Alpha Vault validation results
    """
    print("\n" + "=" * 70)
    print("STRATEGY PERFORMANCE REPORT")
    print("=" * 70)

    print("\n[RETURNS]")
    print(f"  Total Return:         {metrics['total_return']*100:>8.2f}%")
    print(f"  Annual Return:        {metrics['annual_return']*100:>8.2f}%")

    print("\n[RISK-ADJUSTED METRICS]")
    print(f"  Sharpe Ratio:         {metrics['sharpe_ratio']:>8.2f}")
    print(f"  Sortino Ratio:        {metrics['sortino_ratio']:>8.2f}")
    print(f"  Calmar Ratio:         {metrics['calmar_ratio']:>8.2f}")

    print("\n[DRAWDOWN]")
    print(f"  Max Drawdown:         {metrics['max_drawdown']*100:>8.2f}%")
    print(f"  Avg Drawdown:         {metrics['avg_drawdown']*100:>8.2f}%")
    print(f"  Max DD Duration:      {metrics['max_dd_duration_days']:>8.1f} days")

    print("\n[TRADE STATISTICS]")
    print(f"  Total Trades:         {metrics['total_trades']:>8}")
    print(f"  Win Rate:             {metrics['win_rate']*100:>8.2f}%")
    print(f"  Profit Factor:        {metrics['profit_factor']:>8.2f}")
    print(f"  Expectancy:           ${metrics['expectancy']:>8.2f}")
    print(f"  Avg Win:              ${metrics['avg_win']:>8.2f}")
    print(f"  Avg Loss:             ${metrics['avg_loss']:>8.2f}")
    print(f"  Avg Trade Duration:   {metrics['avg_trade_duration_days']:>8.1f} days")

    if validation_report:
        print("\n" + "=" * 70)
        print("ALPHA VAULT VALIDATION")
        print("=" * 70)

        checks = validation_report['checks']
        crit = validation_report['criteria']
        met = validation_report['metrics']

        def status_symbol(passed):
            return "✓ PASS" if passed else "✗ FAIL"

        print(f"\n  Sharpe Ratio > {crit['min_sharpe_ratio']:>4.1f}:  {status_symbol(checks['sharpe_ratio']):>8}  (actual: {met['sharpe_ratio']:.2f})")
        print(f"  Trades > {crit['min_trades']:>6}:     {status_symbol(checks['trade_count']):>8}  (actual: {met['total_trades']})")
        print(f"  Max DD > {crit['max_drawdown']*100:>4.0f}%:      {status_symbol(checks['max_drawdown']):>8}  (actual: {met['max_drawdown']*100:.1f}%)")
        print(f"  Win Rate > {crit['min_win_rate']*100:>3.0f}%:     {status_symbol(checks['win_rate']):>8}  (actual: {met['win_rate']*100:.1f}%)")

        print("\n" + "-" * 70)
        if validation_report['passes']:
            print("✓ STRATEGY PASSES ALL CRITERIA")
            print("\nREADY FOR ALPHA VAULT SUBMISSION")
            print("Next step: Call submit_alpha_telemetry() with these metrics")
        else:
            print("✗ STRATEGY DOES NOT MEET CRITERIA")
            print("\nREFINEMENT NEEDED:")
            if not checks['sharpe_ratio']:
                print("  • Improve risk-adjusted returns")
            if not checks['trade_count']:
                print("  • Increase trade frequency or extend time period")
            if not checks['max_drawdown']:
                print("  • Strengthen risk management")
            if not checks['win_rate']:
                print("  • Refine entry/exit signals")

    print("=" * 70 + "\n")


def plot_results(portfolio, prices):
    """
    Generate visualization of backtest results.

    Parameters:
        portfolio (vbt.Portfolio): Backtest results
        prices (pd.Series): Price data
    """
    # Plot portfolio value over time
    portfolio.plot().show()

    # Plot drawdown
    portfolio.drawdowns.plot().show()

    # Plot trade analysis
    portfolio.trades.plot().show()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function - orchestrates the complete backtest workflow.

    Workflow:
    1. Load data
    2. Generate signals
    3. Run backtest
    4. Calculate metrics
    5. Validate criteria
    6. Print report
    """
    print("\n" + "=" * 70)
    print(f"STRATEGY: {STRATEGY_NAME}")
    print("=" * 70)
    print(f"\nHypothesis: {HYPOTHESIS.strip()}")
    print(f"\nParameters: {PARAMS}")
    print("=" * 70)

    # Step 1: Load data
    print("\n[1/6] Loading market data...")
    prices = load_data()

    if prices is None or len(prices) == 0:
        print("✗ ERROR: Failed to load data")
        return None

    # Step 2: Generate signals
    print("\n[2/6] Generating trading signals...")
    entries, exits = generate_signals(prices, PARAMS)

    entry_count = entries.sum()
    exit_count = exits.sum()

    print(f"  Entry signals: {entry_count}")
    print(f"  Exit signals:  {exit_count}")

    if entry_count == 0:
        print("✗ ERROR: No entry signals generated")
        return None

    # Step 3: Run backtest
    print("\n[3/6] Running backtest simulation...")
    portfolio = run_backtest(prices, entries, exits, BACKTEST_CONFIG)

    # Step 4: Calculate metrics
    print("\n[4/6] Calculating performance metrics...")
    metrics = calculate_metrics(portfolio)

    # Step 5: Validate criteria
    print("\n[5/6] Validating Alpha Vault criteria...")
    passes, validation_report = validate_alpha_vault_criteria(metrics)

    # Step 6: Print report
    print("\n[6/6] Generating performance report...")
    print_performance_report(metrics, validation_report)

    # Return results
    results = {
        'strategy_name': STRATEGY_NAME,
        'hypothesis': HYPOTHESIS,
        'parameters': PARAMS,
        'portfolio': portfolio,
        'metrics': metrics,
        'validation': validation_report,
        'passes_criteria': passes,
    }

    return results


def prepare_alpha_vault_submission(results):
    """
    Prepare data for submit_alpha_telemetry() MCP tool call.

    Parameters:
        results (dict): Output from main()

    Returns:
        dict: Formatted submission data
    """
    if not results or not results['passes_criteria']:
        print("Cannot prepare submission: Strategy does not meet criteria")
        return None

    # Read this file to include code
    with open(__file__, 'r') as f:
        code = f.read()

    submission = {
        'strategy_name': results['strategy_name'],
        'hypothesis': results['hypothesis'],
        'code': code,
        'metrics': results['metrics'],
        'parameters': results['parameters'],
    }

    print("\n" + "=" * 70)
    print("ALPHA VAULT SUBMISSION DATA PREPARED")
    print("=" * 70)
    print("\nCall submit_alpha_telemetry() with the following:")
    print(f"\nstrategy_name: {submission['strategy_name']}")
    print(f"hypothesis: {submission['hypothesis'][:100]}...")
    print(f"metrics: {len(submission['metrics'])} metrics included")
    print(f"parameters: {submission['parameters']}")
    print(f"code: {len(submission['code'])} characters")
    print("=" * 70 + "\n")

    return submission

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Run backtest
    results = main()

    # If successful, prepare submission
    if results and results['passes_criteria']:
        submission = prepare_alpha_vault_submission(results)

        # TODO: Uncomment when ready to submit
        # submit_alpha_telemetry(**submission)

    # Optional: Plot results
    # if results:
    #     plot_results(results['portfolio'], load_data())
