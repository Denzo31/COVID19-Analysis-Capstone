"""
COVID-19 Analysis Package
========================

This package contains modules for comprehensive COVID-19 data analysis including:
- Data preprocessing and cleaning
- Machine learning models (clustering, forecasting, classification)
- Visualization and dashboard creation

Modules:
--------
- data_preprocessing: Functions for data cleaning and feature engineering
- modeling: Machine learning model classes and utilities
- visualization: Plotting and dashboard creation functions

Usage:
------
from src.data_preprocessing import load_covid_data, clean_data
from src.modeling import COVIDClustering, COVIDForecaster, OutbreakPredictor
from src.visualization import COVIDVisualizer

Author: [Your Name]
Course: INSY 8413 | Introduction to Big Data Analytics
Academic Year: 2024-2025, SEM III
"""

__version__ = "1.0.0"
__author__ = "[Your Name]"
__email__ = "[Your Email]"
__course__ = "INSY 8413 | Introduction to Big Data Analytics"

# Package-level imports
from .data_preprocessing import (
    load_covid_data,
    clean_data,
    create_features,
    encode_categorical_variables,
    prepare_modeling_data
)

from .modeling import (
    COVIDClustering,
    COVIDForecaster,
    OutbreakPredictor
)

from .visualization import COVIDVisualizer

__all__ = [
    'load_covid_data',
    'clean_data',
    'create_features',
    'encode_categorical_variables',
    'prepare_modeling_data',
    'COVIDClustering',
    'COVIDForecaster',
    'OutbreakPredictor',
    'COVIDVisualizer'
]