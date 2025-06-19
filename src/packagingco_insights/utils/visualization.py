"""
Visualization utilities for the BI portfolio dashboard.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional, Dict, Any
import pandas as pd


def create_kpi_card(title: str, 
                   value: float, 
                   delta: Optional[float] = None,
                   delta_label: str = "vs previous period",
                   format_type: str = "number",
                   return_html: bool = False) -> Optional[str]:
    """
    Create a KPI card in Streamlit using custom HTML for better layout control.
    If return_html is True, return the HTML string instead of rendering.
    
    Args:
        title: Title of the KPI
        value: Current value
        delta: Change from previous period
        delta_label: Label for the delta
        format_type: Type of formatting ('number', 'currency', 'percentage')
    """
    if format_type == "currency":
        formatted_value = f"${value:,.0f}"
        if delta is not None:
            formatted_delta = f"${delta:+,.0f}"
    elif format_type == "percentage":
        formatted_value = f"{value:.1f}%"
        if delta is not None:
            formatted_delta = f"{delta:+.1f}%"
    else:
        formatted_value = f"{value:,.0f}"
        if delta is not None:
            formatted_delta = f"{delta:+,.0f}"

    # Custom HTML for KPI card (no leading newline or indentation)
    card_html = f"""<div class=\"metric-card\">
    <div style=\"font-size:1.05rem;font-weight:600;margin-bottom:0.25rem;white-space:normal;\">{title}</div>
    <div style=\"font-size:2.1rem;font-weight:700;line-height:1.1;\">{formatted_value}</div>
    {f'<div style=\"font-size:1rem;color:#90caf9;font-weight:500;\">{formatted_delta} <span style=\"font-size:0.85rem;color:#b0bec5;font-weight:400;\">{delta_label}</span></div>' if delta is not None else ''}
</div>"""
    if return_html:
        return card_html
    st.markdown(card_html, unsafe_allow_html=True)
    return None


def format_currency(value: float, currency: str = "USD") -> str:
    """
    Format a number as currency.
    
    Args:
        value: Number to format
        currency: Currency code
    
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${value:,.2f}"
    elif currency == "EUR":
        return f"€{value:,.2f}"
    else:
        return f"{value:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a number as percentage.
    
    Args:
        value: Number to format (0-1 or 0-100)
        decimals: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    # If value is between 0 and 1, multiply by 100
    if 0 <= value <= 1:
        value = value * 100
    
    return f"{value:.{decimals}f}%"


def create_gauge_chart(value: float, 
                      min_val: float, 
                      max_val: float,
                      title: str,
                      color_thresholds: Optional[Dict[str, float]] = None) -> go.Figure:
    """
    Create a gauge chart.
    
    Args:
        value: Current value
        min_val: Minimum value
        max_val: Maximum value
        title: Chart title
        color_thresholds: Dictionary with color thresholds
    
    Returns:
        Plotly figure object
    """
    if color_thresholds is None:
        color_thresholds = {
            'red': 0.6,
            'yellow': 0.8,
            'green': 1.0
        }
    
    # Normalize value to 0-1 range
    normalized_value = (value - min_val) / (max_val - min_val)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': (max_val + min_val) / 2},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val * color_thresholds['red']], 'color': "lightgray"},
                {'range': [max_val * color_thresholds['red'], max_val * color_thresholds['yellow']], 'color': "yellow"},
                {'range': [max_val * color_thresholds['yellow'], max_val], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig


def create_waterfall_chart(data: pd.DataFrame,
                          x_col: str,
                          y_col: str,
                          title: str) -> go.Figure:
    """
    Create a waterfall chart.
    
    Args:
        data: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure(go.Waterfall(
        name="",
        orientation="h",
        measure=["relative"] * len(data),
        x=data[y_col],
        textposition="outside",
        text=data[x_col],
        y=data[x_col],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title=title,
        showlegend=False,
        waterfallgap=0.2,
    )
    
    return fig


def create_heatmap(data: pd.DataFrame,
                  x_col: str,
                  y_col: str,
                  value_col: str,
                  title: str) -> go.Figure:
    """
    Create a heatmap chart.
    
    Args:
        data: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        value_col: Column name for values
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    # Pivot data for heatmap
    pivot_data = data.pivot(index=y_col, columns=x_col, values=value_col)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Viridis'
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title()
    )
    
    return fig


def create_scatter_plot(data: pd.DataFrame,
                       x_col: str,
                       y_col: str,
                       color_col: Optional[str] = None,
                       size_col: Optional[str] = None,
                       title: str = "Scatter Plot") -> go.Figure:
    """
    Create a scatter plot.
    
    Args:
        data: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        color_col: Column name for color coding
        size_col: Column name for size coding
        title: Chart title
    
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    if color_col:
        for color_value in data[color_col].unique():
            subset = data[data[color_col] == color_value]
            fig.add_trace(go.Scatter(
                x=subset[x_col],
                y=subset[y_col],
                mode='markers',
                name=str(color_value),
                marker=dict(
                    size=subset[size_col] if size_col else 10
                )
            ))
    else:
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[y_col],
            mode='markers',
            marker=dict(
                size=data[size_col] if size_col else 10
            )
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col.replace('_', ' ').title(),
        yaxis_title=y_col.replace('_', ' ').title()
    )
    
    return fig


def create_dashboard_header(title: str, subtitle: str = "") -> None:
    """
    Create a dashboard header in Streamlit.
    
    Args:
        title: Main title
        subtitle: Subtitle (optional)
    """
    st.title(title)
    if subtitle:
        st.markdown(f"*{subtitle}*")
    st.markdown("---")


def create_sidebar_filters(data: pd.DataFrame,
                          filter_columns: list) -> Dict[str, Any]:
    """
    Create sidebar filters for the dashboard.
    
    Args:
        data: DataFrame with data
        filter_columns: List of column names to create filters for
    
    Returns:
        Dictionary with filter values
    """
    st.sidebar.header("Filters")
    
    filters = {}
    
    for col in filter_columns:
        if col in data.columns:
            unique_values = sorted(data[col].unique())
            selected = st.sidebar.multiselect(
                f"Select {col.replace('_', ' ').title()}",
                unique_values,
                default=unique_values
            )
            filters[col] = selected
    
    return filters


def apply_filters(data: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply filters to a DataFrame.
    
    Args:
        data: DataFrame to filter
        filters: Dictionary with filter values
    
    Returns:
        Filtered DataFrame
    """
    filtered_data = data.copy()
    
    for col, values in filters.items():
        if col in filtered_data.columns and values:
            filtered_data = filtered_data[filtered_data[col].isin(values)]
    
    return filtered_data 