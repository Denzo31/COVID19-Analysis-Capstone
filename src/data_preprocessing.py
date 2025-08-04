"""
Data Preprocessing Module for COVID-19 Analysis
This module contains functions for cleaning and preprocessing the WHO COVID-19 dataset.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import LabelEncoder


def load_covid_data(file_path):
    """
    Load COVID-19 dataset from CSV file.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
    
    Returns:
    --------
    pd.DataFrame
        Loaded dataset
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        print(f"✅ Dataset loaded successfully! Shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None


def clean_data(df):
    """
    Clean and preprocess the COVID-19 dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw dataset
    
    Returns:
    --------
    pd.DataFrame
        Cleaned dataset
    """
    df_clean = df.copy()
    
    # Standardize column names
    df_clean.columns = df_clean.columns.str.strip().str.replace(' ', '_')
    
    # Convert date column
    df_clean['Date_reported'] = pd.to_datetime(df_clean['Date_reported'])
    
    # Handle missing values in numerical columns
    numerical_cols = ['New_cases', 'Cumulative_cases', 'New_deaths', 'Cumulative_deaths']
    for col in numerical_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(0)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Remove duplicates
    df_clean = df_clean.drop_duplicates()
    
    print(f"✅ Data cleaned. Final shape: {df_clean.shape}")
    return df_clean


def create_features(df):
    """
    Create additional features for analysis.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned dataset
    
    Returns:
    --------
    pd.DataFrame
        Dataset with additional features
    """
    df_features = df.copy()
    
    # Date-based features
    df_features['Year'] = df_features['Date_reported'].dt.year
    df_features['Month'] = df_features['Date_reported'].dt.month
    df_features['Day_of_week'] = df_features['Date_reported'].dt.dayofweek
    df_features['Week_of_year'] = df_features['Date_reported'].dt.isocalendar().week
    
    # Case Fatality Rate
    df_features['Case_Fatality_Rate'] = np.where(
        df_features['Cumulative_cases'] > 0,
        (df_features['Cumulative_deaths'] / df_features['Cumulative_cases']) * 100,
        0
    )
    
    # Growth rates
    df_features = df_features.sort_values(['Country', 'Date_reported'])
    df_features['Cases_Growth_Rate'] = df_features.groupby('Country')['Cumulative_cases'].pct_change() * 100
    df_features['Deaths_Growth_Rate'] = df_features.groupby('Country')['Cumulative_deaths'].pct_change() * 100
    
    # Rolling averages
    df_features['New_cases_7day_avg'] = df_features.groupby('Country')['New_cases'].rolling(7, min_periods=1).mean().reset_index(0, drop=True)
    df_features['New_deaths_7day_avg'] = df_features.groupby('Country')['New_deaths'].rolling(7, min_periods=1).mean().reset_index(0, drop=True)
    
    # Pandemic phases
    def get_pandemic_phase(date):
        if date < '2020-06-01':
            return 'Early_Phase'
        elif date < '2021-01-01':
            return 'First_Wave'
        elif date < '2022-01-01':
            return 'Vaccination_Phase'
        else:
            return 'Endemic_Phase'
    
    df_features['Pandemic_Phase'] = df_features['Date_reported'].apply(get_pandemic_phase)
    
    print("✅ Features created successfully")
    return df_features


def encode_categorical_variables(df, categorical_vars=None):
    """
    Encode categorical variables using LabelEncoder.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataset with categorical variables
    categorical_vars : list, optional
        List of categorical variables to encode
    
    Returns:
    --------
    tuple
        (encoded_dataframe, label_encoders_dict)
    """
    if categorical_vars is None:
        categorical_vars = ['Country', 'WHO_region', 'Pandemic_Phase']
    
    df_encoded = df.copy()
    label_encoders = {}
    
    for var in categorical_vars:
        if var in df_encoded.columns:
            le = LabelEncoder()
            df_encoded[f'{var}_encoded'] = le.fit_transform(df_encoded[var])
            label_encoders[var] = le
    
    print(f"✅ Encoded {len(label_encoders)} categorical variables")
    return df_encoded, label_encoders


def prepare_modeling_data(df):
    """
    Prepare data for machine learning models.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Feature-engineered dataset
    
    Returns:
    --------
    pd.DataFrame
        Modeling-ready dataset
    """
    modeling_data = df.copy()
    
    # Remove infinite values
    modeling_data = modeling_data.replace([np.inf, -np.inf], np.nan)
    modeling_data = modeling_data.dropna()
    
    print(f"✅ Modeling data prepared. Shape: {modeling_data.shape}")
    return modeling_data


if __name__ == "__main__":
    # Example usage
    print("COVID-19 Data Preprocessing Module")
    print("This module provides functions for data cleaning and feature engineering.")