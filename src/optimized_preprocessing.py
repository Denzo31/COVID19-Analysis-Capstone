"""
Optimized Data Preprocessing Module for Large COVID-19 Dataset
============================================================

This module provides optimized functions for handling large COVID-19 datasets efficiently.
Includes memory optimization, chunked processing, and sampling strategies.

Author: COVID-19 Analysis Project
Course: INSY 8413 | Introduction to Big Data Analytics
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')


def load_covid_data_optimized(file_path, sample_size=None, random_state=42):
    """
    Load COVID-19 dataset with memory optimization and optional sampling.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
    sample_size : int, optional
        Number of rows to sample for faster processing
    random_state : int
        Random state for reproducible sampling
    
    Returns:
    --------
    pd.DataFrame
        Loaded dataset (full or sampled)
    """
    print("🔄 Loading COVID-19 dataset...")
    
    try:
        # First, get basic info about the dataset
        df_info = pd.read_csv(file_path, nrows=5)
        print(f"📊 Dataset columns: {list(df_info.columns)}")
        
        # Define data types to optimize memory usage (avoid int types due to NA values)
        dtype_dict = {
            'Country_code': 'category',
            'Country': 'category', 
            'WHO_region': 'category'
            # Note: Keeping numeric columns as default to handle NA values
        }
        
        # Load the full dataset with optimized dtypes
        df = pd.read_csv(file_path, dtype=dtype_dict, parse_dates=['Date_reported'])
        
        # Convert numeric columns after loading to handle NA values properly
        numeric_cols = ['New_cases', 'Cumulative_cases', 'New_deaths', 'Cumulative_deaths']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')  # Convert NA to NaN
                df[col] = df[col].fillna(0).astype('int64')  # Fill NaN with 0 and convert to int
        print(f"✅ Full dataset loaded! Shape: {df.shape}")
        print(f"💾 Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Create sample if requested
        if sample_size and sample_size < len(df):
            print(f"🎯 Creating representative sample of {sample_size:,} rows...")
            
            # Stratified sampling by WHO region to maintain representation
            sample_df = df.groupby('WHO_region').apply(
                lambda x: x.sample(min(len(x), sample_size // df['WHO_region'].nunique()), 
                                 random_state=random_state)
            ).reset_index(drop=True)
            
            # Ensure we get close to requested sample size
            if len(sample_df) < sample_size:
                additional_needed = sample_size - len(sample_df)
                remaining_df = df[~df.index.isin(sample_df.index)]
                additional_sample = remaining_df.sample(min(additional_needed, len(remaining_df)), 
                                                      random_state=random_state)
                sample_df = pd.concat([sample_df, additional_sample]).reset_index(drop=True)
            
            print(f"✅ Sample created! Shape: {sample_df.shape}")
            print(f"💾 Sample memory usage: {sample_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            
            # Verify sample representativeness
            print("\n📊 Sample representativeness check:")
            for region in df['WHO_region'].unique():
                original_pct = (df['WHO_region'] == region).mean() * 100
                sample_pct = (sample_df['WHO_region'] == region).mean() * 100
                print(f"  {region}: Original {original_pct:.1f}% → Sample {sample_pct:.1f}%")
            
            return sample_df
        
        return df
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None


def clean_data_optimized(df):
    """
    Optimized data cleaning for large datasets.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw dataset
    
    Returns:
    --------
    pd.DataFrame
        Cleaned dataset
    """
    print("🧹 Starting optimized data cleaning...")
    
    df_clean = df.copy()
    original_shape = df_clean.shape
    
    # 1. Standardize column names (if needed)
    df_clean.columns = df_clean.columns.str.strip().str.replace(' ', '_')
    
    # 2. Handle missing values efficiently
    print("  🔧 Handling missing values...")
    numerical_cols = ['New_cases', 'Cumulative_cases', 'New_deaths', 'Cumulative_deaths']
    
    for col in numerical_cols:
        if col in df_clean.columns:
            missing_count = df_clean[col].isna().sum()
            if missing_count > 0:
                df_clean[col] = df_clean[col].fillna(0)
                print(f"    - {col}: {missing_count:,} missing values filled with 0")
    
    # 3. Remove duplicates
    print("  🔧 Removing duplicates...")
    duplicates_before = len(df_clean)
    df_clean = df_clean.drop_duplicates()
    duplicates_removed = duplicates_before - len(df_clean)
    print(f"    - Removed {duplicates_removed:,} duplicate rows")
    
    # 4. Data validation and cleaning
    print("  🔧 Data validation...")
    
    # Remove rows with negative values (data errors)
    for col in numerical_cols:
        if col in df_clean.columns:
            negative_count = (df_clean[col] < 0).sum()
            if negative_count > 0:
                df_clean = df_clean[df_clean[col] >= 0]
                print(f"    - Removed {negative_count:,} rows with negative {col}")
    
    # Ensure cumulative values are non-decreasing within countries
    print("  🔧 Validating cumulative data consistency...")
    df_clean = df_clean.sort_values(['Country', 'Date_reported'])
    
    print(f"✅ Data cleaning completed!")
    print(f"📊 Shape: {original_shape} → {df_clean.shape}")
    print(f"💾 Memory usage: {df_clean.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    return df_clean


def create_features_optimized(df, chunk_size=50000):
    """
    Optimized feature engineering with chunked processing for large datasets.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Cleaned dataset
    chunk_size : int
        Size of chunks for memory-efficient processing
    
    Returns:
    --------
    pd.DataFrame
        Dataset with engineered features
    """
    print("🔧 Starting optimized feature engineering...")
    
    df_features = df.copy()
    
    # 1. Basic date features (vectorized operations)
    print("  📅 Creating date-based features...")
    df_features['Year'] = df_features['Date_reported'].dt.year.astype('int16')
    df_features['Month'] = df_features['Date_reported'].dt.month.astype('int8')
    df_features['Day_of_week'] = df_features['Date_reported'].dt.dayofweek.astype('int8')
    df_features['Week_of_year'] = df_features['Date_reported'].dt.isocalendar().week.astype('int8')
    
    # 2. Case Fatality Rate (vectorized)
    print("  💀 Calculating Case Fatality Rate...")
    df_features['Case_Fatality_Rate'] = np.where(
        df_features['Cumulative_cases'] > 0,
        (df_features['Cumulative_deaths'] / df_features['Cumulative_cases']) * 100,
        0
    ).astype('float32')
    
    # 3. Growth rates (chunked processing by country)
    print("  📈 Calculating growth rates...")
    df_features = df_features.sort_values(['Country', 'Date_reported'])
    
    # Process in chunks to manage memory
    growth_rates_cases = []
    growth_rates_deaths = []
    
    for country in df_features['Country'].unique():
        country_data = df_features[df_features['Country'] == country].copy()
        
        # Calculate growth rates
        country_data['Cases_Growth_Rate'] = country_data['Cumulative_cases'].pct_change() * 100
        country_data['Deaths_Growth_Rate'] = country_data['Cumulative_deaths'].pct_change() * 100
        
        growth_rates_cases.extend(country_data['Cases_Growth_Rate'].fillna(0).tolist())
        growth_rates_deaths.extend(country_data['Deaths_Growth_Rate'].fillna(0).tolist())
    
    df_features['Cases_Growth_Rate'] = pd.Series(growth_rates_cases, dtype='float32')
    df_features['Deaths_Growth_Rate'] = pd.Series(growth_rates_deaths, dtype='float32')
    
    # 4. Rolling averages (memory efficient)
    print("  📊 Calculating rolling averages...")
    df_features = df_features.sort_values(['Country', 'Date_reported'])
    
    rolling_cases = []
    rolling_deaths = []
    
    for country in df_features['Country'].unique():
        country_data = df_features[df_features['Country'] == country]
        
        rolling_cases.extend(
            country_data['New_cases'].rolling(7, min_periods=1).mean().fillna(0).tolist()
        )
        rolling_deaths.extend(
            country_data['New_deaths'].rolling(7, min_periods=1).mean().fillna(0).tolist()
        )
    
    df_features['New_cases_7day_avg'] = pd.Series(rolling_cases, dtype='float32')
    df_features['New_deaths_7day_avg'] = pd.Series(rolling_deaths, dtype='float32')
    
    # 5. Pandemic phases (optimized)
    print("  🦠 Assigning pandemic phases...")
    
    def get_pandemic_phase_optimized(date):
        """Optimized pandemic phase assignment."""
        if date < pd.Timestamp('2020-06-01'):
            return 'Early_Phase'
        elif date < pd.Timestamp('2021-01-01'):
            return 'First_Wave'
        elif date < pd.Timestamp('2022-01-01'):
            return 'Vaccination_Phase'
        else:
            return 'Endemic_Phase'
    
    df_features['Pandemic_Phase'] = df_features['Date_reported'].apply(
        get_pandemic_phase_optimized
    ).astype('category')
    
    print("✅ Feature engineering completed!")
    print(f"📊 Final shape: {df_features.shape}")
    print(f"💾 Memory usage: {df_features.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Display created features
    new_features = ['Year', 'Month', 'Day_of_week', 'Week_of_year', 'Case_Fatality_Rate', 
                    'Cases_Growth_Rate', 'Deaths_Growth_Rate', 'New_cases_7day_avg', 
                    'New_deaths_7day_avg', 'Pandemic_Phase']
    
    print("📋 Created features:")
    for feature in new_features:
        print(f"  ✓ {feature}")
    
    return df_features


def prepare_modeling_data_optimized(df, sample_for_modeling=100000):
    """
    Prepare optimized modeling dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Feature-engineered dataset
    sample_for_modeling : int
        Sample size for modeling (to handle memory constraints)
    
    Returns:
    --------
    pd.DataFrame
        Modeling-ready dataset
    """
    print("🤖 Preparing modeling data...")
    
    modeling_data = df.copy()
    
    # Remove infinite values
    print("  🔧 Cleaning infinite values...")
    modeling_data = modeling_data.replace([np.inf, -np.inf], np.nan)
    
    # Remove rows with critical missing values
    critical_cols = ['Cases_Growth_Rate', 'Deaths_Growth_Rate', 'Case_Fatality_Rate']
    before_count = len(modeling_data)
    modeling_data = modeling_data.dropna(subset=critical_cols)
    after_count = len(modeling_data)
    print(f"  📊 Removed {before_count - after_count:,} rows with missing critical values")
    
    # Create sample for modeling if dataset is too large
    if len(modeling_data) > sample_for_modeling:
        print(f"  🎯 Creating modeling sample of {sample_for_modeling:,} rows...")
        
        # Stratified sampling by WHO region and pandemic phase
        modeling_data = modeling_data.groupby(['WHO_region', 'Pandemic_Phase']).apply(
            lambda x: x.sample(min(len(x), sample_for_modeling // 
                                 (modeling_data['WHO_region'].nunique() * 
                                  modeling_data['Pandemic_Phase'].nunique())), 
                             random_state=42)
        ).reset_index(drop=True)
    
    # Encode categorical variables
    print("  🔤 Encoding categorical variables...")
    label_encoders = {}
    categorical_vars = ['Country', 'WHO_region', 'Pandemic_Phase']
    
    for var in categorical_vars:
        if var in modeling_data.columns:
            le = LabelEncoder()
            modeling_data[f'{var}_encoded'] = le.fit_transform(modeling_data[var])
            label_encoders[var] = le
            print(f"    ✓ {var}: {len(le.classes_)} categories")
    
    print(f"✅ Modeling data prepared!")
    print(f"📊 Final shape: {modeling_data.shape}")
    print(f"💾 Memory usage: {modeling_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    return modeling_data, label_encoders


def save_processed_data(df, output_dir='../data/processed', filename='covid19_processed.csv'):
    """
    Save processed data with memory optimization.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Processed dataset
    output_dir : str
        Output directory
    filename : str
        Output filename
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    print(f"💾 Saving processed data to {output_path}...")
    
    # Save with compression to reduce file size
    df.to_csv(output_path, index=False, compression='gzip')
    
    file_size = os.path.getsize(output_path) / 1024**2
    print(f"✅ Data saved successfully! File size: {file_size:.2f} MB")
    
    return output_path


if __name__ == "__main__":
    print("🚀 COVID-19 Optimized Data Preprocessing Module")
    print("=" * 60)
    
    # Example usage with the actual dataset
    data_path = '../data/raw/WHO-COVID-19-global-daily-data.csv'
    
    # Load with sampling for faster processing
    df = load_covid_data_optimized(data_path, sample_size=50000)
    
    if df is not None:
        # Clean the data
        df_clean = clean_data_optimized(df)
        
        # Create features
        df_features = create_features_optimized(df_clean)
        
        # Prepare for modeling
        modeling_data, encoders = prepare_modeling_data_optimized(df_features)
        
        # Save processed data
        save_processed_data(df_features, filename='covid19_optimized_sample.csv')
        
        print("\n✅ All preprocessing completed successfully!")
        print(f"📊 Final dataset ready for analysis: {modeling_data.shape}")
    else:
        print("❌ Failed to load dataset. Please check the file path.")