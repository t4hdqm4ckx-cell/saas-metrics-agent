# Skill: Visualization

**Category**: Frontend / Presentation  
**Version**: 1.0  
**Owner**: Frontend Engineering

---

## Overview
The Visualization skill governs chart type selection, rendering configuration, color application, and accessibility for all charts in the FlowSync dashboard. Charts are implemented using Chart.js 4.x with custom plugin configurations.

---

## Design System

### Color Palette (Dark Mode)
```css
--bg-primary:     #0D1117   /* Page background */
--bg-card:        #161B22   /* Card / panel background */
--bg-elevated:    #1C2128   /* Hover states, dropdowns */
--border:         #30363D   /* Card borders */
--text-primary:   #E6EDF3   /* Main text */
--text-secondary: #8B949E   /* Labels, subtitles */
--text-muted:     #484F58   /* Disabled, placeholder */

/* Accent colors (electric) */
--cyan:           #00D4FF   /* Primary — MRR, revenue */
--purple:         #A855F7   /* Secondary — customers */
--green:          #00FF94   /* Success — growth, NRR */
--amber:          #F59E0B   /* Warning — churn, CAC */
--red:            #FF4757   /* Danger — high churn */
--indigo:         #6366F1   /* Engagement metrics */
--pink:           #EC4899   /* Trial conversion */

/* Gradients */
--grad-cyan:      linear-gradient(135deg, #00D4FF, #0EA5E9)
--grad-purple:    linear-gradient(135deg, #A855F7, #7C3AED)
--grad-green:     linear-gradient(135deg, #00FF94, #10B981)
--grad-amber:     linear-gradient(135deg, #F59E0B, #EF4444)
```

---

## Chart Type Specifications

### 1. MRR Trend — Area Chart
- **Type**: `line` with `fill: true`
- **Color**: Cyan (`#00D4FF`) with 20% opacity fill
- **Use case**: Show MRR growth over 24 months
- **Annotations**: Add vertical line at "Today" marker
- **Tooltip**: Show MRR, MoM change %, YoY change %

### 2. MRR Waterfall — Bar Chart (Stacked)
- **Type**: `bar` (stacked, floating bars for waterfall effect)
- **Colors**: 
  - New MRR: Green (`#00FF94`)
  - Expansion MRR: Cyan (`#00D4FF`)
  - Contraction MRR: Amber (`#F59E0B`)
  - Churned MRR: Red (`#FF4757`)
- **Use case**: Decompose MRR movement each month

### 3. Revenue by Plan — Donut Chart
- **Type**: `doughnut`
- **Colors**: Cyan (Starter), Purple (Pro), Green (Business)
- **Center label**: Total MRR (custom Chart.js plugin)
- **Use case**: Show revenue mix across subscription tiers

### 4. Customer Growth — Grouped Bar
- **Type**: `bar` (grouped)
- **Colors**: New customers (Green), Churned (Red)
- **Use case**: Net customer additions by month

### 5. Churn Rate Trend — Line Chart
- **Type**: `line`
- **Color**: Amber (`#F59E0B`) → Red (`#FF4757`) via gradient
- **Reference line**: Target churn rate (3%) as dashed line
- **Use case**: Churn rate over time vs. target

### 6. Trial Conversion Funnel — Horizontal Bar
- **Type**: `bar` (horizontal, `indexAxis: 'y'`)
- **Colors**: Sequential from Purple to Cyan (progressive)
- **Stages**: Trial Starts → Activated → Day-7 Retained → Converted → Paid Month 2
- **Use case**: Visualize trial-to-paid funnel drop-off

### 7. Cohort Retention Heatmap — Custom Grid
- **Type**: Custom (CSS grid + JavaScript rendering, not native Chart.js)
- **Color scale**: 0% = `#FF4757` (red), 50% = `#F59E0B` (amber), 100% = `#00FF94` (green)
- **Axes**: Y = cohort month, X = months since acquisition (0–12)
- **Use case**: Retention rates per acquisition cohort

### 8. MAU/DAU Trend — Dual-axis Line
- **Type**: `line` (two datasets)
- **Colors**: MAU = Indigo, DAU = Cyan
- **Y-axis**: Shared left axis; stickiness ratio on right axis
- **Use case**: Track user engagement over time

### 9. LTV:CAC Ratio — Bar Chart
- **Type**: `bar`
- **Color**: Gradient from Amber (ratio < 3) to Green (ratio > 5)
- **Reference lines**: 3× (minimum target, red dashed), 5× (healthy, green dashed)
- **Use case**: Unit economics health over time

### 10. Payback Period — Area Chart
- **Type**: `line` with fill
- **Color**: Purple (`#A855F7`)
- **Reference line**: 12-month target (amber dashed)
- **Use case**: Track CAC payback period trend

---

## Chart Configuration Defaults

```javascript
const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
        duration: 800,
        easing: 'easeInOutQuart'
    },
    plugins: {
        legend: {
            labels: {
                color: '#8B949E',
                font: { family: "'Inter', sans-serif", size: 12 },
                usePointStyle: true,
                pointStyleWidth: 8
            }
        },
        tooltip: {
            backgroundColor: '#1C2128',
            borderColor: '#30363D',
            borderWidth: 1,
            titleColor: '#E6EDF3',
            bodyColor: '#8B949E',
            padding: 12,
            cornerRadius: 8
        }
    },
    scales: {
        x: {
            grid: { color: 'rgba(48, 54, 61, 0.5)' },
            ticks: { color: '#8B949E', font: { size: 11 } }
        },
        y: {
            grid: { color: 'rgba(48, 54, 61, 0.5)' },
            ticks: { color: '#8B949E', font: { size: 11 } }
        }
    }
};
```

---

## Accessibility

- All charts include `aria-label` on the `<canvas>` element
- Color choices maintain WCAG AA contrast ratios on dark backgrounds
- Tooltips are keyboard-accessible via Tab + Enter
- Charts include `role="img"` and descriptive `aria-describedby` paragraphs
- Do not rely solely on color to convey meaning — use patterns or labels where possible

---

## Responsive Breakpoints

| Breakpoint | Chart Height | Grid Columns |
|-----------|-------------|-------------|
| < 768px (mobile) | 200px | 1 |
| 768–1024px (tablet) | 280px | 2 |
| > 1024px (desktop) | 320–400px | 2–3 |
| > 1440px (large) | 400px | 3 |

---

## Performance Guidelines

- Lazy-render charts that are not in the visible tab
- Destroy and recreate chart instances when switching tabs (prevents memory leaks)
- Cap displayed data points at 24 (one per month); do not render weekly data
- Use `devicePixelRatio` scaling for retina displays

---

*Last updated: 2026-06-01*
