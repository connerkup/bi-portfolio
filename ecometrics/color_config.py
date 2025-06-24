"""
Centralized color configuration for EcoMetrics app.
Provides a consistent color palette across all visualizations.
"""

# Monochrome Pastel Color Palette
# Based on blue-grey tones with subtle variations for easy-on-the-eyes visuals

# Primary colors (main brand colors)
PRIMARY_BLUE = "#7BA7CC"  # Soft blue-grey
PRIMARY_LIGHT = "#A8C5E6"  # Light pastel blue
PRIMARY_DARK = "#5A7A9A"   # Darker blue-grey

# Secondary colors (accent colors)
SECONDARY_GREY = "#B8C5D1"  # Soft grey-blue
SECONDARY_LIGHT = "#D1DCE8"  # Very light pastel
SECONDARY_DARK = "#8A9BA8"   # Medium grey-blue

# Neutral colors
NEUTRAL_LIGHT = "#F5F7FA"   # Very light background
NEUTRAL_MEDIUM = "#E8EDF2"  # Light grey background
NEUTRAL_DARK = "#6B7A8A"    # Dark grey text

# Status colors (for indicators and alerts)
SUCCESS_COLOR = "#9BC5A3"   # Soft pastel green
WARNING_COLOR = "#E6C27D"   # Soft pastel yellow
ERROR_COLOR = "#D4A5A5"     # Soft pastel red
INFO_COLOR = "#A8C5E6"      # Light blue (same as primary light)

# Monochrome colors for single-metric charts
MONOCHROME_COLORS = [
    PRIMARY_BLUE,      # #7BA7CC - Main blue
    "#8A9BA8",         # #8A9BA8 - Medium grey-blue
    "#A8C5E6",         # #A8C5E6 - Light blue
    "#B8C5D1",         # #B8C5D1 - Soft grey-blue
    "#5A7A9A",         # #5A7A9A - Dark blue-grey
    "#D1DCE8",         # #D1DCE8 - Very light pastel
]

# Distinct colors for comparison charts (multi-line, multi-category)
COMPARISON_COLORS = [
    "#7BA7CC",  # Blue
    "#E6C27D",  # Yellow
    "#9BC5A3",  # Green
    "#D4A5A5",  # Red
    "#C4B5D1",  # Purple
    "#F4A261",  # Orange
    "#264653",  # Dark blue
    "#2A9D8F",  # Teal
    "#E76F51",  # Coral
    "#8B5A96",  # Lavender
]

# Chart color sequences - Default to comparison colors for better differentiation
CHART_COLORS = COMPARISON_COLORS

# Sequential colors for single-metric charts (gradients)
SEQUENTIAL_COLORS = [
    "#D1DCE8",  # Very light
    "#B8C5D1",  # Light
    "#A8C5E6",  # Medium light
    "#7BA7CC",  # Medium
    "#8A9BA8",  # Medium dark
    "#5A7A9A",  # Dark
]

# Diverging colors for positive/negative comparisons
DIVERGING_COLORS = [
    "#D4A5A5",  # Soft red (negative)
    "#E6C27D",  # Soft yellow (neutral)
    "#9BC5A3",  # Soft green (positive)
]

# Heat map colors - Green to Red (for performance metrics, emissions, etc.)
HEAT_COLORS_GREEN_RED = [
    "#9BC5A3",  # Light green (good)
    "#E6C27D",  # Yellow (neutral)
    "#D4A5A5",  # Light red (poor)
]

# Heat map colors - Blue to Red (for temperature-like metrics)
HEAT_COLORS_BLUE_RED = [
    "#7BA7CC",  # Blue (cold/low)
    "#E6C27D",  # Yellow (neutral)
    "#D4A5A5",  # Red (hot/high)
]

# Heat map colors - Sequential Blue (for single-metric heat maps)
HEAT_COLORS_BLUE = [
    "#D1DCE8",  # Very light blue
    "#B8C5D1",  # Light blue
    "#A8C5E6",  # Medium light blue
    "#7BA7CC",  # Medium blue
    "#5A7A9A",  # Dark blue
]

# Heat map colors - Sequential Green (for positive metrics)
HEAT_COLORS_GREEN = [
    "#E8F5E8",  # Very light green
    "#C8E6C8",  # Light green
    "#A5D6A5",  # Medium light green
    "#9BC5A3",  # Medium green
    "#6B8E6B",  # Dark green
]

# Heat map colors - Sequential Red (for negative metrics)
HEAT_COLORS_RED = [
    "#FFEBEE",  # Very light red
    "#FFCDD2",  # Light red
    "#EF9A9A",  # Medium light red
    "#D4A5A5",  # Medium red
    "#B71C1C",  # Dark red
]

# Performance indicator colors (for KPIs, status indicators)
PERFORMANCE_COLORS = {
    "excellent": "#9BC5A3",  # Green
    "good": "#A8C5E6",       # Blue
    "average": "#E6C27D",    # Yellow
    "poor": "#D4A5A5",       # Red
    "critical": "#B71C1C",   # Dark red
}

# Sustainability colors (for ESG metrics)
SUSTAINABILITY_COLORS = {
    "recycled": "#9BC5A3",      # Green
    "renewable": "#A8C5E6",     # Blue
    "emissions": "#D4A5A5",     # Red
    "waste": "#E6C27D",         # Yellow
    "water": "#7BA7CC",         # Blue
    "energy": "#F4A261",        # Orange
}

# Financial colors (for financial metrics)
FINANCIAL_COLORS = {
    "revenue": "#9BC5A3",       # Green (positive)
    "profit": "#A8C5E6",        # Blue
    "cost": "#D4A5A5",          # Red (negative)
    "margin": "#E6C27D",        # Yellow
    "growth": "#2A9D8F",        # Teal
    "decline": "#E76F51",       # Coral
}

# Altair color scheme
ALTAIR_COLOR_SCHEME = "category10"  # Use Altair's built-in category scheme for better differentiation

# Plotly color sequence
PLOTLY_COLORS = CHART_COLORS

# CSS color variables for styling
CSS_COLORS = {
    "primary": PRIMARY_BLUE,
    "primary-light": PRIMARY_LIGHT,
    "primary-dark": PRIMARY_DARK,
    "secondary": SECONDARY_GREY,
    "secondary-light": SECONDARY_LIGHT,
    "secondary-dark": SECONDARY_DARK,
    "neutral-light": NEUTRAL_LIGHT,
    "neutral-medium": NEUTRAL_MEDIUM,
    "neutral-dark": NEUTRAL_DARK,
    "success": SUCCESS_COLOR,
    "warning": WARNING_COLOR,
    "error": ERROR_COLOR,
    "info": INFO_COLOR,
}

# Function to get color by index (for cycling through colors)
def get_color_by_index(index: int) -> str:
    """Get a color from the palette by index, cycling through available colors."""
    return CHART_COLORS[index % len(CHART_COLORS)]

# Function to get a subset of colors
def get_color_subset(count: int) -> list:
    """Get a subset of colors for a specific number of categories."""
    if count <= len(CHART_COLORS):
        return CHART_COLORS[:count]
    else:
        # If we need more colors than available, cycle through
        return [get_color_by_index(i) for i in range(count)]

# Function to get comparison colors (ensures good differentiation)
def get_comparison_colors(count: int) -> list:
    """Get colors optimized for comparison charts with good differentiation."""
    if count <= len(COMPARISON_COLORS):
        return COMPARISON_COLORS[:count]
    else:
        # If we need more colors than available, cycle through
        return [COMPARISON_COLORS[i % len(COMPARISON_COLORS)] for i in range(count)]

# Function to get monochrome colors for single-metric charts
def get_monochrome_colors(count: int) -> list:
    """Get monochrome colors for single-metric charts."""
    if count <= len(MONOCHROME_COLORS):
        return MONOCHROME_COLORS[:count]
    else:
        # If we need more colors than available, cycle through
        return [MONOCHROME_COLORS[i % len(MONOCHROME_COLORS)] for i in range(count)]

# Function to get sequential colors for single-metric charts
def get_sequential_colors(count: int) -> list:
    """Get sequential colors for single-metric charts (gradients)."""
    if count <= len(SEQUENTIAL_COLORS):
        return SEQUENTIAL_COLORS[:count]
    else:
        # If we need more colors than available, cycle through
        return [SEQUENTIAL_COLORS[i % len(SEQUENTIAL_COLORS)] for i in range(count)]

# Function to get diverging colors for positive/negative comparisons
def get_diverging_colors() -> list:
    """Get diverging colors for positive/negative comparisons."""
    return DIVERGING_COLORS.copy()

# Function to get heat map colors
def get_heat_colors(style: str = "green_red", count: int = 5) -> list:
    """Get standardized heat map colors.
    
    Args:
        style: "green_red", "blue_red", "blue", "green", "red"
        count: number of color steps (default 5)
    """
    if style == "green_red":
        colors = HEAT_COLORS_GREEN_RED
    elif style == "blue_red":
        colors = HEAT_COLORS_BLUE_RED
    elif style == "blue":
        colors = HEAT_COLORS_BLUE
    elif style == "green":
        colors = HEAT_COLORS_GREEN
    elif style == "red":
        colors = HEAT_COLORS_RED
    else:
        colors = HEAT_COLORS_GREEN_RED  # Default
    
    if count <= len(colors):
        return colors[:count]
    else:
        # Interpolate colors if we need more
        return get_gradient_colors(colors[0], colors[-1], count)

# Function to get performance colors
def get_performance_color(level: str) -> str:
    """Get color for performance level."""
    return PERFORMANCE_COLORS.get(level.lower(), NEUTRAL_DARK)

# Function to get sustainability colors
def get_sustainability_color(metric: str) -> str:
    """Get color for sustainability metric."""
    return SUSTAINABILITY_COLORS.get(metric.lower(), PRIMARY_BLUE)

# Function to get financial colors
def get_financial_color(metric: str) -> str:
    """Get color for financial metric."""
    return FINANCIAL_COLORS.get(metric.lower(), PRIMARY_BLUE)

# Function to get gradient colors
def get_gradient_colors(start_color: str = PRIMARY_LIGHT, end_color: str = PRIMARY_DARK, steps: int = 5) -> list:
    """Generate a gradient between two colors."""
    import colorsys
    
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    
    colors = []
    for i in range(steps):
        t = i / (steps - 1)
        interpolated_rgb = tuple(start_rgb[j] + t * (end_rgb[j] - start_rgb[j]) for j in range(3))
        colors.append(rgb_to_hex(interpolated_rgb))
    
    return colors 