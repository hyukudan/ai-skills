---
name: data-visualization
description: |
  Data visualization best practices and patterns. Covers chart selection,
  storytelling with data, matplotlib, plotly, dashboard design, and
  principles for effective visual communication.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [visualization, charts, matplotlib, plotly, dashboards, data-storytelling]
category: data/visualization
trigger_phrases:
  - "data visualization"
  - "chart"
  - "graph"
  - "plot"
  - "matplotlib"
  - "plotly"
  - "dashboard"
  - "visualize data"
  - "data storytelling"
variables:
  library:
    type: string
    description: Visualization library
    enum: [matplotlib, plotly, seaborn, altair]
    default: matplotlib
  purpose:
    type: string
    description: Visualization purpose
    enum: [exploration, presentation, dashboard]
    default: exploration
---

# Data Visualization Guide

## Core Philosophy

**Every visualization should answer a question.** If you can't state what question your chart answers, you don't need that chart.

> "The purpose of visualization is insight, not pictures." — Ben Shneiderman

---

## Chart Selection Guide

```
What are you showing?
│
├── Comparison
│   ├── Few categories → Bar chart
│   ├── Many categories → Horizontal bar
│   └── Over time → Line chart
│
├── Distribution
│   ├── Single variable → Histogram
│   ├── Compare distributions → Box plot
│   └── Density → Violin plot
│
├── Relationship
│   ├── Two variables → Scatter plot
│   ├── With categories → Colored scatter
│   └── Many variables → Pair plot
│
├── Composition
│   ├── Parts of whole → Pie (sparingly) / Stacked bar
│   ├── Over time → Stacked area
│   └── Hierarchical → Treemap
│
└── Trend
    ├── Time series → Line chart
    ├── With uncertainty → Line + confidence band
    └── Multiple series → Multi-line / Small multiples
```

---

## 1. Matplotlib Essentials

{% if library == "matplotlib" %}

### Basic Setup

```python
import matplotlib.pyplot as plt
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')

# Figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# DPI for crisp output
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
```

### Line Charts

```python
# Basic line chart
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(dates, values, label='Sales', color='#2563eb', linewidth=2)
ax.fill_between(dates, values, alpha=0.1, color='#2563eb')

ax.set_xlabel('Date')
ax.set_ylabel('Sales ($)')
ax.set_title('Monthly Sales Trend')
ax.legend()

# Rotate x-axis labels
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('sales_trend.png', bbox_inches='tight')
```

### Bar Charts

```python
# Grouped bar chart
categories = ['Q1', 'Q2', 'Q3', 'Q4']
product_a = [100, 120, 90, 150]
product_b = [80, 100, 110, 130]

x = np.arange(len(categories))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar(x - width/2, product_a, width, label='Product A', color='#2563eb')
bars2 = ax.bar(x + width/2, product_b, width, label='Product B', color='#16a34a')

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax.annotate(f'{height}',
                xy=(bar.get_x() + bar.get_width()/2, height),
                ha='center', va='bottom')
```

### Scatter Plots

```python
fig, ax = plt.subplots(figsize=(10, 8))

# Scatter with size and color
scatter = ax.scatter(
    df['x'],
    df['y'],
    s=df['size'] * 10,          # Point size
    c=df['category'].astype('category').cat.codes,  # Color by category
    cmap='viridis',
    alpha=0.7
)

ax.set_xlabel('X Variable')
ax.set_ylabel('Y Variable')
plt.colorbar(scatter, label='Category')
```

### Subplots and Layouts

```python
# Grid of plots
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

for i, (ax, col) in enumerate(zip(axes.flat, columns)):
    ax.hist(df[col], bins=30, edgecolor='white')
    ax.set_title(col)

plt.tight_layout()

# Different sized subplots
fig = plt.figure(figsize=(12, 8))
gs = fig.add_gridspec(2, 3)

ax1 = fig.add_subplot(gs[0, :])  # Top row, all columns
ax2 = fig.add_subplot(gs[1, 0])  # Bottom left
ax3 = fig.add_subplot(gs[1, 1:]) # Bottom right (2 columns)
```

{% endif %}

---

## 2. Plotly for Interactive Charts

{% if library == "plotly" %}

### Basic Setup

```python
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set default template
import plotly.io as pio
pio.templates.default = "plotly_white"
```

### Line Charts

```python
# Simple line chart
fig = px.line(
    df,
    x='date',
    y='value',
    color='category',
    title='Sales Over Time'
)

fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Sales ($)',
    hovermode='x unified'
)

fig.show()

# With confidence interval
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['upper'],
    mode='lines',
    line=dict(width=0),
    showlegend=False
))

fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['lower'],
    mode='lines',
    line=dict(width=0),
    fill='tonexty',
    fillcolor='rgba(68, 68, 68, 0.2)',
    showlegend=False
))

fig.add_trace(go.Scatter(
    x=df['date'],
    y=df['value'],
    mode='lines',
    name='Value'
))
```

### Interactive Bar Charts

```python
fig = px.bar(
    df,
    x='category',
    y='value',
    color='segment',
    barmode='group',
    text='value',
    title='Sales by Category'
)

fig.update_traces(textposition='outside')
fig.update_layout(uniformtext_minsize=8)
```

### Dashboard Layout

```python
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=('Revenue', 'Users', 'Conversion', 'Churn'),
    specs=[
        [{"type": "scatter"}, {"type": "bar"}],
        [{"type": "pie"}, {"type": "scatter"}]
    ]
)

fig.add_trace(go.Scatter(x=dates, y=revenue), row=1, col=1)
fig.add_trace(go.Bar(x=categories, y=users), row=1, col=2)
fig.add_trace(go.Pie(labels=labels, values=values), row=2, col=1)
fig.add_trace(go.Scatter(x=dates, y=churn), row=2, col=2)

fig.update_layout(height=800, showlegend=False)
```

{% endif %}

---

## 3. Design Principles

### Color Palette

```python
# Categorical (distinct groups)
CATEGORICAL = ['#2563eb', '#16a34a', '#dc2626', '#9333ea', '#f59e0b']

# Sequential (ordered values)
SEQUENTIAL = ['#eff6ff', '#bfdbfe', '#60a5fa', '#2563eb', '#1d4ed8']

# Diverging (positive/negative)
DIVERGING = ['#dc2626', '#fca5a5', '#f5f5f5', '#86efac', '#16a34a']

# Colorblind-safe palette
COLORBLIND_SAFE = ['#0077bb', '#33bbee', '#009988', '#ee7733', '#cc3311']
```

### Typography and Labels

```python
# Clear, informative titles
ax.set_title('Monthly Revenue Growth (YoY %)', fontsize=14, fontweight='bold')

# Axis labels with units
ax.set_xlabel('Date')
ax.set_ylabel('Revenue ($M)')

# Remove chartjunk
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Annotations for key points
ax.annotate(
    'Product Launch',
    xy=(launch_date, peak_value),
    xytext=(launch_date, peak_value * 1.1),
    arrowprops=dict(arrowstyle='->', color='gray'),
    fontsize=10
)
```

### Small Multiples

```python
# Faceted plots for comparison
fig, axes = plt.subplots(2, 3, figsize=(15, 10), sharey=True)

for ax, region in zip(axes.flat, regions):
    data = df[df['region'] == region]
    ax.plot(data['date'], data['value'])
    ax.set_title(region)

# Consistent y-axis makes comparison easy
plt.suptitle('Sales by Region', fontsize=14)
plt.tight_layout()
```

---

## 4. Common Chart Types

### Distribution Visualization

```python
import seaborn as sns

# Histogram with KDE
fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(df['value'], kde=True, ax=ax)
ax.axvline(df['value'].mean(), color='red', linestyle='--', label='Mean')
ax.axvline(df['value'].median(), color='green', linestyle='--', label='Median')
ax.legend()

# Box plot comparison
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(data=df, x='category', y='value', ax=ax)

# Violin plot (distribution + density)
fig, ax = plt.subplots(figsize=(10, 6))
sns.violinplot(data=df, x='category', y='value', ax=ax)
```

### Time Series

```python
# Multiple metrics with different scales
fig, ax1 = plt.subplots(figsize=(12, 6))

# Primary axis
color1 = '#2563eb'
ax1.set_xlabel('Date')
ax1.set_ylabel('Revenue ($)', color=color1)
ax1.plot(df['date'], df['revenue'], color=color1, label='Revenue')
ax1.tick_params(axis='y', labelcolor=color1)

# Secondary axis
ax2 = ax1.twinx()
color2 = '#16a34a'
ax2.set_ylabel('Users', color=color2)
ax2.plot(df['date'], df['users'], color=color2, label='Users')
ax2.tick_params(axis='y', labelcolor=color2)

fig.tight_layout()
```

### Heatmaps

```python
# Correlation matrix
fig, ax = plt.subplots(figsize=(10, 8))

corr_matrix = df.select_dtypes(include=[np.number]).corr()

sns.heatmap(
    corr_matrix,
    annot=True,
    fmt='.2f',
    cmap='RdBu_r',
    center=0,
    ax=ax,
    square=True
)

ax.set_title('Feature Correlation Matrix')
```

---

## 5. Dashboard Design

### Layout Principles

```
┌────────────────────────────────────────────────────┐
│  TITLE / DATE RANGE                          FILTERS│
├────────────────────────────────────────────────────┤
│  KPI 1   │  KPI 2   │  KPI 3   │  KPI 4           │
├──────────┴──────────┴──────────┴──────────────────┤
│                                                    │
│              MAIN CHART (60% of space)             │
│                                                    │
├──────────────────────────┬─────────────────────────┤
│  SUPPORTING CHART 1      │  SUPPORTING CHART 2     │
│                          │                         │
└──────────────────────────┴─────────────────────────┘
```

### KPI Cards

```python
def create_kpi_card(value, label, change_pct, ax):
    """Create a KPI card visualization."""
    ax.text(0.5, 0.7, f'{value:,.0f}', fontsize=28, ha='center', fontweight='bold')
    ax.text(0.5, 0.4, label, fontsize=12, ha='center', color='gray')

    # Change indicator
    color = 'green' if change_pct >= 0 else 'red'
    arrow = '↑' if change_pct >= 0 else '↓'
    ax.text(0.5, 0.15, f'{arrow} {abs(change_pct):.1f}%', fontsize=14, ha='center', color=color)

    ax.axis('off')
```

---

## 6. Storytelling with Data

### Narrative Structure

1. **Context**: What's the situation?
2. **Conflict**: What's the problem/opportunity?
3. **Resolution**: What does the data reveal?
4. **Action**: What should we do?

### Annotation Strategy

```python
# Highlight key insights
ax.annotate(
    'Sales dropped 40% during\nlockdown period',
    xy=(lockdown_start, lockdown_value),
    xytext=(lockdown_start - 30, lockdown_value + 1000),
    fontsize=10,
    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2'),
    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
)

# Use color to direct attention
ax.fill_between(dates[highlight_start:highlight_end],
                values[highlight_start:highlight_end],
                color='#fef3c7', alpha=0.5)
```

---

## Quick Reference

### Chart Selection Matrix

| Data Type | Comparison | Distribution | Relationship |
|-----------|------------|--------------|--------------|
| Categorical | Bar | - | Grouped bar |
| Numeric | Line | Histogram | Scatter |
| Time | Line | - | Line |
| Geographic | Choropleth | - | - |

### Dos and Don'ts

| DO | DON'T |
|----|-------|
| Start y-axis at 0 for bars | Truncate y-axis to exaggerate |
| Use consistent colors | Rainbow every chart |
| Label axes clearly | Assume units are obvious |
| Highlight key insights | Show all data equally |
| Use white space | Cram in too much |

### Export for Different Uses

```python
# For presentations (high res)
plt.savefig('chart.png', dpi=300, bbox_inches='tight')

# For web (smaller file)
plt.savefig('chart.png', dpi=100, bbox_inches='tight')

# Vector format (scalable)
plt.savefig('chart.svg', format='svg', bbox_inches='tight')

# For print (CMYK PDF)
plt.savefig('chart.pdf', format='pdf', bbox_inches='tight')
```

---

## Related Skills

- `pandas-data-analysis` - Data preparation for visualization
- `dashboard-design` - Interactive dashboard patterns
- `presentation-skills` - Presenting data effectively
