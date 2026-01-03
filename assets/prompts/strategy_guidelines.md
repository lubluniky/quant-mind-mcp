# Strategy Development Guidelines

## Purpose

This document provides comprehensive guidelines for developing valid, robust quantitative trading strategies for the QuantMind Alpha Vault. Use these guidelines to ensure your strategies are well-designed, properly tested, and production-ready.

---

## Table of Contents

1. [Strategy Validity Criteria](#strategy-validity-criteria)
2. [Common Pitfalls](#common-pitfalls)
3. [Metrics Interpretation](#metrics-interpretation)
4. [Strategy Types & Examples](#strategy-types--examples)
5. [Testing & Validation](#testing--validation)
6. [Risk Management](#risk-management)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## Strategy Validity Criteria

### Alpha Vault Submission Requirements

For a strategy to be accepted into the Alpha Vault, it must meet ALL of the following criteria:

#### 1. Sharpe Ratio > 1.5

**Definition**: Risk-adjusted return metric measuring excess return per unit of volatility.

**Formula**:
```
Sharpe Ratio = (Annual Return - Risk-Free Rate) / Annual Volatility
```

**Why it matters**:
- Sharpe > 1.5 indicates strong risk-adjusted performance
- Shows the strategy generates returns efficiently relative to risk
- Industry standard for institutional-quality strategies

**How to improve**:
- Reduce strategy volatility (smoother equity curve)
- Increase returns without proportionally increasing risk
- Add filters to avoid low-quality trades
- Implement position sizing based on volatility

#### 2. Total Trades > 100

**Definition**: Minimum number of completed trades during backtest period.

**Why it matters**:
- Ensures statistical significance of results
- Prevents lucky outcomes from small sample sizes
- Validates strategy robustness across multiple market conditions

**How to improve**:
- Extend backtest time period
- Reduce entry threshold strictness
- Trade multiple symbols or timeframes
- Adjust signal generation frequency

**Warning**: Don't artificially inflate trade count through overtrading - maintain strategy logic integrity.

#### 3. Maximum Drawdown > -30%

**Definition**: Largest peak-to-trough decline in portfolio value.

**Formula**:
```
Max Drawdown = (Trough Value - Peak Value) / Peak Value
```

**Why it matters**:
- Measures worst-case loss scenario
- Tests psychological and capital sustainability
- Critical for risk management and capital allocation

**How to improve**:
- Implement stop-loss mechanisms
- Add position sizing based on risk
- Use volatility filters to avoid choppy markets
- Diversify across uncorrelated signals
- Add regime detection to pause trading in adverse conditions

#### 4. Win Rate > 45%

**Definition**: Percentage of profitable trades out of total trades.

**Formula**:
```
Win Rate = (Winning Trades / Total Trades) × 100
```

**Why it matters**:
- Indicates signal accuracy
- Affects psychological tradability
- Balances with profit factor for overall expectancy

**How to improve**:
- Tighten entry conditions (more selective)
- Implement confirmation signals
- Add filters to avoid low-probability setups
- Optimize exit logic to protect profits

**Note**: High win rate isn't everything - profit factor matters more. A 40% win rate with 2:1 reward-risk can be excellent.

### Secondary Quality Indicators

While not strict requirements, these metrics indicate strategy quality:

- **Profit Factor > 1.5**: Ratio of gross profits to gross losses
- **Sortino Ratio > 2.0**: Downside deviation-adjusted returns
- **Calmar Ratio > 0.5**: Return / Max Drawdown ratio
- **Average Trade Duration**: Reasonable holding periods (not too short/long)
- **Expectancy > 0**: Positive expected value per trade

---

## Common Pitfalls

### 1. Overfitting (Curve Fitting)

**What it is**: Optimizing strategy to fit historical data perfectly, losing predictive power.

**Warning signs**:
- Strategy has 10+ parameters
- Performance degrades dramatically with small parameter changes
- Excellent in-sample, poor out-of-sample results
- Complex rules with many conditions

**How to avoid**:
- Limit parameters (prefer 3-5 maximum)
- Use simple, economically logical rules
- Test on out-of-sample data
- Employ walk-forward analysis
- Prefer strategies that work across parameter ranges

**Example of overfitting**:
```python
# BAD: Too many specific conditions
if (rsi < 29.3 and volume > 1.23 * avg_volume and
    price < bb_lower * 0.987 and hour == 10 and
    day_of_week == 2):
    enter_trade()

# GOOD: Simple, logical rule
if rsi < 30 and price < bb_lower:
    enter_trade()
```

### 2. Lookahead Bias

**What it is**: Using future information in past decisions.

**Common causes**:
- Using non-shifted data (e.g., `prices` instead of `prices.shift(1)`)
- Calculating indicators on same-bar data used for entry
- Using end-of-period data for intra-period decisions

**How to avoid**:
- Always use `.shift(1)` when comparing signals to prices
- Ensure indicators are calculated on prior bars only
- Be careful with resampling and forward-filling data

**Example**:
```python
# BAD: Lookahead bias
entries = prices > prices.rolling(20).mean()

# GOOD: No lookahead bias
ma = prices.rolling(20).mean()
entries = prices.shift(1) > ma.shift(1)
```

### 3. Data Snooping

**What it is**: Testing many strategies on the same data until finding one that works.

**Warning signs**:
- Testing 50+ strategy variations
- Cherry-picking best-performing variant
- No theoretical justification for strategy

**How to avoid**:
- Start with hypothesis before testing
- Limit number of variations tested
- Use separate data for validation
- Document all tested strategies (not just winners)
- Apply multiple testing corrections (e.g., Bonferroni)

### 4. Survivorship Bias

**What it is**: Only testing on securities that survived to present day.

**Impact**: Overestimates returns by excluding failed companies.

**How to avoid**:
- Use survivorship-bias-free datasets
- Include delisted securities in backtests
- Be aware when using index constituents
- Note limitation in strategy documentation

### 5. Ignoring Transaction Costs

**What it is**: Backtesting without realistic trading costs.

**Components to include**:
- **Commission**: Brokerage fees (minimum 0.1%)
- **Slippage**: Difference between expected and actual fill (0.05-0.1%)
- **Spread**: Bid-ask spread cost
- **Market Impact**: Price movement from large orders

**How to include**:
```python
portfolio = vbt.Portfolio.from_signals(
    close=prices,
    entries=entries,
    exits=exits,
    fees=0.001,      # 0.1% commission
    slippage=0.0005, # 0.05% slippage
)
```

### 6. Insufficient Testing Period

**What it is**: Testing on too short a time period or limited market conditions.

**Minimum recommendations**:
- **Time period**: 3+ years of data
- **Market regimes**: Include bull, bear, and sideways markets
- **Volatility regimes**: Test in high and low volatility periods

**How to validate**:
- Split data into multiple periods
- Test on different market conditions
- Use walk-forward analysis
- Verify consistency across regimes

### 7. Ignoring Risk Management

**What it is**: Focusing only on returns without considering risk.

**Essential risk controls**:
- Position sizing (don't risk >2% per trade)
- Stop losses (protect against catastrophic loss)
- Maximum portfolio drawdown limits
- Concentration limits (diversification)
- Leverage constraints

### 8. Data Quality Issues

**Common problems**:
- Missing data (NaN values)
- Outliers from data errors
- Incorrect corporate action adjustments
- Timezone inconsistencies

**How to handle**:
```python
# Clean data before backtesting
prices = prices.dropna()
prices = prices[(prices > 0) & (prices < prices.quantile(0.99))]
prices = prices[~prices.duplicated()]
```

---

## Metrics Interpretation

### Return Metrics

#### Total Return
- **Interpretation**: Cumulative profit/loss over entire period
- **Good**: > 20% for multi-year backtest
- **Excellent**: > 50%
- **Warning**: Low returns may not justify risk

#### Annual Return
- **Interpretation**: Annualized rate of return
- **Good**: > 15%
- **Excellent**: > 30%
- **Note**: Must be evaluated alongside risk metrics

### Risk-Adjusted Metrics

#### Sharpe Ratio
- **Formula**: `(Return - RiskFreeRate) / Volatility`
- **Interpretation**:
  - < 1.0: Poor risk-adjusted returns
  - 1.0 - 1.5: Acceptable
  - 1.5 - 2.0: Good (Alpha Vault minimum: 1.5)
  - \> 2.0: Excellent
  - \> 3.0: Exceptional (verify for overfitting)

#### Sortino Ratio
- **Formula**: `(Return - RiskFreeRate) / Downside Deviation`
- **Interpretation**: Like Sharpe but only penalizes downside volatility
- **Better metric** for strategies with asymmetric returns
- **Good**: > 1.5
- **Excellent**: > 2.0

#### Calmar Ratio
- **Formula**: `Annual Return / Max Drawdown`
- **Interpretation**: Return per unit of maximum loss
- **Good**: > 0.5
- **Excellent**: > 1.0
- **Note**: Especially important for drawdown-sensitive investors

### Drawdown Metrics

#### Maximum Drawdown
- **Interpretation**: Worst peak-to-trough decline
- **Acceptable**: < -30% (Alpha Vault maximum)
- **Good**: < -20%
- **Excellent**: < -15%
- **Warning**: > -40% may be psychologically unacceptable

#### Average Drawdown
- **Interpretation**: Typical drawdown magnitude
- **Good**: < -10%
- **Note**: Should be much smaller than max drawdown

#### Max Drawdown Duration
- **Interpretation**: Longest time underwater (below previous peak)
- **Acceptable**: < 6 months
- **Good**: < 3 months
- **Warning**: > 1 year may lead to strategy abandonment

### Trade Statistics

#### Win Rate
- **Interpretation**: Percentage of profitable trades
- **Minimum**: > 45% (Alpha Vault requirement)
- **Good**: > 50%
- **Excellent**: > 60%
- **Note**: High win rate isn't essential if profit factor is good

#### Profit Factor
- **Formula**: `Gross Profit / Gross Loss`
- **Interpretation**:
  - < 1.0: Losing strategy
  - 1.0 - 1.5: Marginal
  - 1.5 - 2.0: Good
  - \> 2.0: Excellent

#### Expectancy
- **Formula**: `(Win Rate × Avg Win) - (Loss Rate × Avg Loss)`
- **Interpretation**: Expected profit per trade
- **Minimum**: > 0 (positive expectancy)
- **Good**: > 1% of account
- **Note**: Higher is better, but consider trade frequency

#### Average Trade Duration
- **Interpretation**: Typical holding period
- **Considerations**:
  - Too short: High transaction costs, possibly noise trading
  - Too long: Capital inefficiency, limited opportunities
  - Optimal: Depends on strategy type (scalping vs. swing trading)

### Trade Count

#### Total Trades
- **Minimum**: > 100 (Alpha Vault requirement)
- **Good**: > 200
- **Excellent**: > 500
- **Warning**:
  - Too few: Statistically insignificant
  - Too many: May indicate overtrading

---

## Strategy Types & Examples

### 1. Mean Reversion Strategies

**Hypothesis**: Prices revert to mean after extreme deviations.

**Common Approaches**:
- Z-score based entries
- Bollinger Band bounces
- RSI oversold/overbought
- Pairs trading (cointegration)

**Example Logic**:
```python
z_score = (price - rolling_mean) / rolling_std
entries = z_score < -2.0  # Oversold
exits = z_score > -0.5    # Revert to mean
```

**Best Markets**: Range-bound, low-trending environments

**Key Metrics**:
- High win rate (60%+)
- Moderate Sharpe (1.5-2.5)
- Short holding periods

### 2. Momentum/Trend Following

**Hypothesis**: Trends persist due to behavioral factors.

**Common Approaches**:
- Moving average crossovers
- Breakout strategies
- Relative strength
- Time series momentum

**Example Logic**:
```python
fast_ma = price.rolling(10).mean()
slow_ma = price.rolling(50).mean()
entries = fast_ma > slow_ma
exits = fast_ma < slow_ma
```

**Best Markets**: Trending, directional movements

**Key Metrics**:
- Lower win rate (40-50%)
- High profit factor (2.0+)
- Longer holding periods

### 3. Statistical Arbitrage

**Hypothesis**: Statistical relationships create profit opportunities.

**Common Approaches**:
- Pairs trading
- Basket trading
- Cointegration-based
- Cross-asset arbitrage

**Example Logic**:
```python
spread = price_a - hedge_ratio * price_b
z_score = (spread - spread_mean) / spread_std
entries_long = z_score < -2.0
entries_short = z_score > 2.0
```

**Best Markets**: Efficient markets with stable relationships

**Key Metrics**:
- Very high win rate (70%+)
- Low returns per trade
- High frequency

### 4. Volatility-Based Strategies

**Hypothesis**: Volatility clustering creates opportunities.

**Common Approaches**:
- Volatility breakout
- Range expansion/contraction
- ATR-based entries
- VIX strategies

**Example Logic**:
```python
atr = calculate_atr(high, low, close)
volatility_breakout = (high - low) > atr * 1.5
entries = volatility_breakout
```

**Best Markets**: Volatile, regime-changing environments

**Key Metrics**:
- Moderate win rate (50-55%)
- Large wins when correct
- Variable holding periods

### 5. Multi-Factor Strategies

**Hypothesis**: Combining factors improves performance.

**Common Approaches**:
- Value + Momentum
- Trend + Mean Reversion filters
- Technical + Fundamental
- Multi-timeframe confirmation

**Example Logic**:
```python
# Combine trend and mean reversion
trend_up = fast_ma > slow_ma
oversold = rsi < 30
entries = trend_up & oversold  # Only buy dips in uptrend
```

**Best Markets**: All market types (adaptive)

**Key Metrics**:
- Balanced performance
- Higher Sharpe ratios
- More consistent returns

---

## Testing & Validation

### Walk-Forward Analysis

**Purpose**: Test strategy robustness over time.

**Process**:
1. Divide data into windows (e.g., 1 year training, 3 months testing)
2. Optimize parameters on training window
3. Test on forward (unseen) period
4. Roll window forward and repeat
5. Aggregate results across all periods

**Passing Criteria**:
- Out-of-sample Sharpe > 70% of in-sample Sharpe
- Consistent performance across windows
- No dramatic degradation over time

### Monte Carlo Simulation

**Purpose**: Assess statistical significance of results.

**Process**:
1. Randomly shuffle trade order
2. Calculate metrics for shuffled trades
3. Repeat 1000+ times
4. Compare actual results to distribution

**Passing Criteria**:
- Actual Sharpe in top 5% of shuffled results
- p-value < 0.05 for key metrics

### Parameter Sensitivity Analysis

**Purpose**: Ensure strategy isn't overfit to specific parameters.

**Process**:
1. Test strategy across range of parameter values
2. Create heatmap of Sharpe ratios
3. Identify stable regions

**Passing Criteria**:
- Positive Sharpe across 70%+ of parameter space
- No sharp dropoffs near optimal parameters
- Plateau region around optimal values

### Out-of-Sample Testing

**Purpose**: Validate on completely unseen data.

**Process**:
1. Reserve 20-30% of data for final validation
2. Develop strategy on remaining data
3. Lock parameters and test on reserved data

**Passing Criteria**:
- OOS Sharpe > 1.0
- OOS return > 0
- Similar metric profile to in-sample

---

## Risk Management

### Position Sizing

**Fixed Fractional**:
```python
position_size = account_value * risk_per_trade / stop_loss_distance
```

**Kelly Criterion**:
```python
kelly_fraction = (win_rate * avg_win - loss_rate * avg_loss) / avg_win
position_size = kelly_fraction * 0.5  # Use half-Kelly for safety
```

**Volatility-Based**:
```python
target_volatility = 0.15  # 15% annual
position_size = target_volatility / strategy_volatility
```

### Stop Losses

**Fixed Percentage**:
```python
stop_loss = entry_price * (1 - 0.02)  # 2% stop
```

**ATR-Based (Volatility-Adjusted)**:
```python
stop_loss = entry_price - (atr * 2.0)  # 2x ATR stop
```

**Time-Based**:
```python
# Exit after N days regardless of P/L
max_holding_period = 5
```

### Portfolio Constraints

**Maximum Position Size**: 10-20% per trade

**Maximum Drawdown Limit**: Pause trading if DD > threshold

**Correlation Limits**: Avoid highly correlated positions

**Leverage Limits**: Maximum 2x leverage for most strategies

---

## Troubleshooting Guide

### Problem: Sharpe Ratio Too Low (< 1.5)

**Potential Causes**:
- High volatility relative to returns
- Poor trade selection
- Inadequate risk management

**Solutions**:
1. Add volatility filters (avoid choppy markets)
2. Implement stricter entry conditions
3. Use volatility-based position sizing
4. Add profit targets and stops
5. Filter trades by quality metrics

### Problem: Not Enough Trades (< 100)

**Potential Causes**:
- Entry conditions too strict
- Backtest period too short
- Low-frequency strategy

**Solutions**:
1. Extend backtest time period
2. Relax entry threshold slightly
3. Trade multiple symbols
4. Use lower timeframe data
5. Reduce required confirmations

### Problem: Maximum Drawdown Too Large (< -30%)

**Potential Causes**:
- No stop losses
- Position sizing too aggressive
- Poor losing trade management

**Solutions**:
1. Implement stop losses (2-5% per trade)
2. Reduce position size
3. Add maximum portfolio drawdown limit
4. Exit losing trades faster
5. Add market regime filters

### Problem: Win Rate Too Low (< 45%)

**Potential Causes**:
- Poor entry timing
- Premature exits
- Inadequate signal quality

**Solutions**:
1. Add confirmation signals
2. Improve exit logic (let winners run)
3. Filter trades by additional conditions
4. Optimize entry threshold
5. Avoid choppy/ranging markets

### Problem: Suspicious Results (Too Good)

**Warning Signs**:
- Sharpe > 4.0
- Win rate > 80%
- No losing periods

**Check For**:
1. Lookahead bias
2. Data quality issues
3. Overfitting
4. Missing transaction costs
5. Incorrect signal logic

**Action**: Review code carefully, verify data integrity

### Problem: Poor Out-of-Sample Performance

**Causes**:
- Overfitting
- Parameter optimization on too much data
- Regime change
- Data snooping

**Solutions**:
1. Simplify strategy (reduce parameters)
2. Use walk-forward analysis
3. Test across multiple time periods
4. Add regime detection/filtering
5. Accept that some degradation is normal

---

## Checklist Before Submission

Before calling `submit_alpha_telemetry()`, verify:

### Code Quality
- [ ] No hard-coded dates or symbols (parameterized)
- [ ] Proper error handling
- [ ] Clear comments and documentation
- [ ] Code runs without errors
- [ ] All imports included

### Data Integrity
- [ ] No NaN values in signals
- [ ] No lookahead bias
- [ ] Data quality validated
- [ ] Proper timezone handling
- [ ] Survivorship bias considered

### Backtest Validity
- [ ] Transaction costs included (min 0.1%)
- [ ] Slippage modeled (min 0.05%)
- [ ] Realistic position sizing
- [ ] Proper time delays (no same-bar execution)
- [ ] 3+ years of data tested

### Performance Criteria
- [ ] Sharpe Ratio > 1.5
- [ ] Total Trades > 100
- [ ] Max Drawdown > -30%
- [ ] Win Rate > 45%

### Risk Management
- [ ] Stop losses implemented or considered
- [ ] Position sizing appropriate
- [ ] Drawdown limits defined
- [ ] Risk per trade < 5%

### Robustness Testing
- [ ] Out-of-sample validation performed
- [ ] Parameter sensitivity tested
- [ ] Multiple market regimes included
- [ ] Walk-forward analysis conducted

### Documentation
- [ ] Clear hypothesis stated
- [ ] Parameters documented
- [ ] Metrics calculated correctly
- [ ] Known limitations noted

---

## Additional Resources

### Recommended Reading

**Books**:
- "Quantitative Trading" by Ernie Chan
- "Algorithmic Trading" by Ernest Chan
- "Advances in Financial Machine Learning" by Marcos López de Prado
- "Evidence-Based Technical Analysis" by David Aronson

**Papers**:
- "The Deflated Sharpe Ratio" (Bailey & López de Prado)
- "Pseudo-Mathematics and Financial Charlatanism" (Taleb)
- "The Probability of Backtest Overfitting" (Bailey et al.)

### Statistical Concepts

**Key Topics**:
- Multiple testing problem
- Statistical significance
- Type I/II errors
- Confidence intervals
- P-hacking awareness

### Useful Formulas

**Sharpe Ratio**:
```
SR = √(252) × mean(daily_returns) / std(daily_returns)
```

**Maximum Drawdown**:
```
DD = (Trough - Peak) / Peak
```

**Win Rate**:
```
WR = Wins / Total_Trades
```

**Profit Factor**:
```
PF = Gross_Profit / Gross_Loss
```

**Expectancy**:
```
E = (WR × AvgWin) - ((1-WR) × AvgLoss)
```

---

## Final Thoughts

Developing profitable trading strategies is both art and science. These guidelines provide a framework, but market conditions evolve and strategies must adapt.

**Key Principles**:

1. **Simplicity**: Simple strategies are more robust
2. **Logic**: Always have economic rationale
3. **Rigor**: Test thoroughly, question everything
4. **Honesty**: Don't fool yourself with data snooping
5. **Risk**: Protect capital first, profits second
6. **Iteration**: Learn from failures, refine successes

Remember: **A strategy that passes all criteria but has no logical foundation is likely data-mined. A strategy with strong logic that fails criteria needs refinement, not abandonment.**

Good luck with your quantitative research!
