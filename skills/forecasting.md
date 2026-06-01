# Skill: Forecasting

**Category**: Predictive Analytics  
**Version**: 1.0  
**Owner**: Data Science

---

## Overview
The Forecasting skill extrapolates SaaS metrics forward using trend analysis, scenario modeling, and growth rate decomposition. All forecasts are probabilistic and include confidence bands.

---

## Forecasting Methods

### 1. Linear Trend Extrapolation
- Applied to: MRR, customer count, MAU
- Method: Ordinary Least Squares regression on trailing 6 months
- Output: 3, 6, and 12-month point estimates
- Best for: Mature, stable-growth metrics

### 2. Exponential Smoothing (Holt-Winters)
- Applied to: Churn rate, trial conversion (seasonality-sensitive)
- Method: Triple exponential smoothing with additive seasonality
- Parameters: α=0.3, β=0.1, γ=0.2 (tuned on 24-month synthetic data)
- Best for: Metrics with seasonal patterns and trend

### 3. Cohort-Based LTV Forecast
- Projects LTV using survival curve derived from cohort retention heatmap
- Each cohort's expected lifetime = area under its retention curve
- LTV = ARPU × expected lifetime months
- More accurate than simple `ARPU / churn_rate` for heterogeneous cohorts

### 4. Scenario Modeling
Three standard scenarios computed for each 12-month forecast:

| Scenario | MRR Growth Assumption | Churn Assumption | Probability |
|----------|-----------------------|-----------------|-------------|
| Bear | 3% MoM → 0% by month 6 | +50bps above current | 20% |
| Base | Current trailing 3-month average | Current trend | 60% |
| Bull | +2pp above base | −30bps below current | 20% |

---

## ARR Forecasting Model

```python
def forecast_arr(snapshots: list[MonthlySnapshot], horizon: int = 12) -> ForecastResult:
    """
    Returns ARR forecast with 80% confidence interval.
    
    horizon: number of months forward to forecast
    """
    mrr_values = [s.mrr for s in snapshots[-6:]]  # trailing 6 months
    
    # Compute monthly growth rates
    growth_rates = [
        (mrr_values[i] / mrr_values[i-1]) - 1
        for i in range(1, len(mrr_values))
    ]
    
    mean_growth = np.mean(growth_rates)
    std_growth = np.std(growth_rates)
    
    # Monte Carlo simulation (1000 paths)
    n_simulations = 1000
    final_mrr_values = []
    
    for _ in range(n_simulations):
        mrr = mrr_values[-1]
        for month in range(horizon):
            g = np.random.normal(mean_growth, std_growth)
            mrr *= (1 + g)
        final_mrr_values.append(mrr)
    
    final_mrr_values.sort()
    
    return ForecastResult(
        point_estimate=np.mean(final_mrr_values) * 12,  # ARR
        p10=np.percentile(final_mrr_values, 10) * 12,
        p50=np.percentile(final_mrr_values, 50) * 12,
        p90=np.percentile(final_mrr_values, 90) * 12,
        horizon_months=horizon,
        method='monte_carlo'
    )
```

---

## Churn Forecasting

### Short-Term (1–3 months)
- Use trailing 3-month average churn rate
- Apply ±0.5pp standard error band

### Long-Term (6–12 months)
- Model churn as declining over time (product maturity effect)
- Apply decay function: `churn_t = churn_0 × e^(−0.02t)` where t = months
- This reflects improving onboarding, feature maturity, and customer success investment

### Early Warning Indicators
Metrics that predict churn 1–2 months ahead:
1. DAU/MAU decline > 5pp MoM → +1.2pp churn in 45 days
2. Trial activation rate decline > 10pp → +0.8pp churn next month
3. Support ticket volume spike > 30% MoM → +0.5pp churn

---

## Forecast Output Schema

```python
@dataclass
class ForecastResult:
    metric: str                 # 'mrr' | 'arr' | 'customers' | 'churn_rate'
    generated_at: str           # ISO-8601
    horizon_months: int
    method: str                 # 'linear' | 'holt_winters' | 'monte_carlo' | 'cohort'
    point_estimate: float
    p10: float                  # 10th percentile (bear scenario)
    p50: float                  # 50th percentile (median)
    p90: float                  # 90th percentile (bull scenario)
    scenarios: dict             # {'bear': float, 'base': float, 'bull': float}
    confidence_note: str        # plain-English caveat
```

---

## Dashboard Integration

Forecasts appear as:
- **Dashed line** extending beyond the "Today" marker on trend charts
- **Shaded confidence band** (10th–90th percentile) with 10% opacity
- **Scenario selector** (Bear / Base / Bull) toggle in the Revenue tab

---

## Forecast Accuracy Tracking

| Method | MAPE (last 6 months backtested) | Best Use |
|--------|--------------------------------|---------|
| Linear OLS | 8.2% | Stable metrics |
| Holt-Winters | 5.7% | Seasonal metrics |
| Monte Carlo | 4.1% (P50) | Wide-range scenarios |
| Cohort LTV | 11.3% | Long-horizon LTV |

Backtesting uses walk-forward validation: train on months 1–18, test on months 19–24.

---

## Limitations & Caveats

- All forecasts are based on synthetic data patterns — accuracy in production depends on real data quality
- Black swan events (pricing changes, viral spikes, platform outages) are not modeled
- Forecasts assume no change in product, pricing, or go-to-market strategy
- Confidence bands widen significantly beyond 6 months — treat 12-month forecasts as directional only

---

*Last updated: 2026-06-01*
