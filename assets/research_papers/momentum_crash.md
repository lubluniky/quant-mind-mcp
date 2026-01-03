# Momentum Crashes (2016) - Kent Daniel & Tobias Moskowitz

## Abstract

Momentum strategies have identified strong positive returns across asset classes. However, momentum strategies can experience precipitous crashes.

## Key Findings

**Panic States**: Momentum crashes happen when the market rebounds sharply after a period of high panic.

**Option-like Behavior**: The loser portfolio acts like a call option on the market.

**Beta Dynamics**: The beta of the momentum portfolio becomes highly negative during bear markets.

## Mathematical Model

To avoid crashes, one should implement a Dynamic Volatility Scaling:

$$w_t = \frac{\sigma_{target}}{\sigma_{market, t-1}}$$

Where:
- $w_t$ is the position weight at time t
- $\sigma_{target}$ is the target volatility level
- $\sigma_{market, t-1}$ is the realized market volatility

## Implementation Strategy

1. **Monitor Market Regime**: Track market volatility and detect panic states
2. **Dynamic Position Sizing**: Scale positions inversely with volatility
3. **Risk Controls**: Implement stop-losses during high volatility periods
4. **Beta Hedging**: Consider market-neutral implementations

## Empirical Results

- Standard momentum: Sharpe 0.8, Max DD -50%
- Vol-scaled momentum: Sharpe 1.2, Max DD -25%
- Crisis-aware momentum: Sharpe 1.5, Max DD -15%
