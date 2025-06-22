"""
Layout Utilities for EcoMetrics Streamlit App

This module provides utility functions for creating layouts
that work well with Streamlit's native responsive system.
"""

import streamlit as st
from packagingco_insights.utils import create_kpi_card

def create_responsive_columns(num_columns):
    """
    Create columns that adapt to available space.
    
    Args:
        num_columns (int): Number of columns to create
    
    Returns:
        list: List of column objects
    """
    return st.columns(num_columns)

def create_responsive_chart_container(fig, height=400):
    """
    Create a responsive chart container with proper styling.
    
    Args:
        fig: Plotly figure object
        height (int): Chart height in pixels
    
    Returns:
        None: Renders the chart in a responsive container
    """
    fig.update_layout(
        height=height,
        title_x=0.5, # Center title
        margin=dict(t=40, b=10, l=10, r=10) # Reduce margin around chart
    )
    st.plotly_chart(fig, use_container_width=True)

def create_responsive_metric_grid(metrics_data, columns=4):
    """
    Create a responsive grid of metric cards.
    
    Args:
        metrics_data (list): List of tuples (title, value, format_type)
        columns (int): Number of columns to display
    
    Returns:
        None: Renders the metric grid
    """
    cols = create_responsive_columns(min(columns, len(metrics_data)))
    
    for i, (title, value, format_type) in enumerate(metrics_data):
        if i < len(cols):
            with cols[i]:
                create_kpi_card(title, value, format_type=format_type)

def create_responsive_metrics(metrics_data, max_columns=4):
    """
    Create responsive metrics that adapt to available space.
    
    Args:
        metrics_data (list): List of tuples (title, value, format_type)
        max_columns (int): Maximum number of columns to use
    
    Returns:
        None: Renders the metrics
    """
    # Determine how many columns we can actually use
    available_columns = min(max_columns, len(metrics_data))
    cols = create_responsive_columns(available_columns)
    
    # Display metrics using the available columns
    for i, (title, value, format_type) in enumerate(metrics_data):
        if i < len(cols):
            with cols[i]:
                create_kpi_card(title, value, format_type=format_type)
        else:
            # If we have more metrics than columns, display them in a single column
            # This ensures all metrics are shown
            create_kpi_card(title, value, format_type=format_type) 