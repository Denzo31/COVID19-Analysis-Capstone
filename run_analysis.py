#!/usr/bin/env python3
"""
COVID-19 Analysis Capstone Project - Main Execution Script
==========================================================

This script runs the complete COVID-19 analysis pipeline including:
1. Data loading and preprocessing
2. Exploratory data analysis
3. Machine learning models (clustering, forecasting, classification)
4. Visualization generation
5. Results summary

Usage:
    python run_analysis.py

Requirements:
    - All packages from requirements.txt installed
    - Data file in data/raw/WHO-COVID-19-global-daily-data.csv

Author: [Your Name]
Course: INSY 8413 | Introduction to Big Data Analytics
"""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Add src to path for imports
sys.path.append('src')

from src.data_preprocessing import (
    load_covid_data, clean_data, create_features, 
    encode_categorical_variables, prepare_modeling_data
)
from src.modeling import COVIDClustering, COVIDForecaster, OutbreakPredictor
from src.visualization import COVIDVisualizer
import pandas as pd
import numpy as np

def main():
    """
    Main execution function for COVID-19 analysis pipeline.
    """
    print("🦠 COVID-19 Analysis Capstone Project")
    print("=" * 50)
    print("Course: INSY 8413 | Introduction to Big Data Analytics")
    print("Academic Year: 2024-2025, SEM III")
    print("=" * 50)
    
    # Step 1: Data Loading and Preprocessing
    print("\n📂 Step 1: Loading and Preprocessing Data...")
    
    # Load data
    data_path = 'data/raw/WHO-COVID-19-global-daily-data.csv'
    df = load_covid_data(data_path)
    
    if df is None:
        print("❌ Failed to load data. Please check the file path.")
        return
    
    # Clean data
    df_clean = clean_data(df)
    
    # Create features
    df_features = create_features(df_clean)
    
    # Encode categorical variables
    df_encoded, label_encoders = encode_categorical_variables(df_features)
    
    # Prepare modeling data
    modeling_data = prepare_modeling_data(df_encoded)
    
    print(f"✅ Data preprocessing completed. Final shape: {modeling_data.shape}")
    
    # Step 2: Exploratory Data Analysis
    print("\n📊 Step 2: Exploratory Data Analysis...")
    
    # Initialize visualizer
    viz = COVIDVisualizer()
    
    # Global trends
    daily_global = modeling_data.groupby('Date_reported').agg({
        'New_cases': 'sum',
        'New_deaths': 'sum',
        'Cumulative_cases': 'sum',
        'Cumulative_deaths': 'sum'
    })
    
    # Create global trends plot
    viz.plot_global_trends(daily_global, save=True)
    
    # Top countries analysis
    latest_country_data = modeling_data.groupby('Country').agg({
        'Cumulative_cases': 'max',
        'Cumulative_deaths': 'max',
        'WHO_region': 'first',
        'Case_Fatality_Rate': 'last'
    }).reset_index()
    
    viz.plot_top_countries(latest_country_data, save=True)
    
    # Correlation analysis
    numerical_vars = ['New_cases', 'New_deaths', 'Cumulative_cases', 'Cumulative_deaths',
                      'Case_Fatality_Rate', 'Cases_Growth_Rate', 'Deaths_Growth_Rate']
    viz.plot_correlation_matrix(modeling_data, numerical_vars, save=True)
    
    print("✅ Exploratory data analysis completed.")
    
    # Step 3: Machine Learning Models
    print("\n🤖 Step 3: Machine Learning Models...")
    
    # Clustering Analysis
    print("\n🎯 Running Clustering Analysis...")
    country_features = modeling_data.groupby('Country').agg({
        'Cumulative_cases': 'max',
        'Cumulative_deaths': 'max',
        'Case_Fatality_Rate': 'mean',
        'Cases_Growth_Rate': 'mean',
        'Deaths_Growth_Rate': 'mean'
    }).reset_index()
    
    # Filter countries with sufficient data
    country_features = country_features[country_features['Cumulative_cases'] >= 1000]
    
    # Clustering
    clustering_features = ['Cumulative_cases', 'Cumulative_deaths', 'Case_Fatality_Rate',
                          'Cases_Growth_Rate', 'Deaths_Growth_Rate']
    X_cluster = country_features[clustering_features].fillna(0)
    
    clusterer = COVIDClustering()
    cluster_labels = clusterer.fit_predict(X_cluster)
    country_features['Cluster'] = cluster_labels
    
    # Visualize clustering results
    viz.plot_clustering_results(country_features, save=True)
    
    # Time Series Forecasting
    print("\n📈 Running Time Series Forecasting...")
    global_daily = modeling_data.groupby('Date_reported').agg({
        'New_cases': 'sum',
        'New_deaths': 'sum'
    }).reset_index().sort_values('Date_reported')
    
    forecaster = COVIDForecaster()
    ts_features = forecaster.create_time_features(global_daily)
    forecast_results = forecaster.train(ts_features)
    
    # Visualize forecasting results
    test_data = forecast_results['test_data']
    viz.plot_forecasting_results(
        test_data['y_cases_test'].index,
        test_data['y_cases_test'].values,
        test_data['cases_pred'],
        'Cases',
        save=True
    )
    
    # Outbreak Prediction
    print("\n🚨 Running Outbreak Prediction...")
    outbreak_data = modeling_data[modeling_data['Cases_Growth_Rate'].notna()].copy()
    
    predictor = OutbreakPredictor()
    outbreak_data = predictor.create_risk_labels(outbreak_data)
    
    outbreak_features = ['New_cases', 'New_deaths', 'Cumulative_cases', 'Cumulative_deaths',
                        'Case_Fatality_Rate', 'New_cases_7day_avg', 'New_deaths_7day_avg',
                        'WHO_region_encoded', 'Month', 'Year']
    
    X_outbreak = outbreak_data[outbreak_features].fillna(0)
    y_outbreak = outbreak_data['Outbreak_Risk']
    
    outbreak_results = predictor.train(X_outbreak, y_outbreak)
    
    print("✅ Machine learning models completed.")
    
    # Step 4: Results Summary
    print("\n📋 Step 4: Generating Results Summary...")
    
    # Calculate summary statistics
    summary_stats = {
        'total_cases': int(modeling_data['Cumulative_cases'].max()),
        'total_deaths': int(modeling_data['Cumulative_deaths'].max()),
        'countries': int(modeling_data['Country'].nunique()),
        'global_cfr': float(modeling_data['Cumulative_deaths'].max() / modeling_data['Cumulative_cases'].max() * 100),
        'clusters': int(clusterer.n_clusters),
        'accuracy': float(outbreak_results['accuracy'] * 100)
    }
    
    # Create dashboard summary
    viz.create_dashboard_summary(summary_stats, save=True)
    
    # Print final results
    print("\n🎉 ANALYSIS COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("📊 FINAL RESULTS SUMMARY:")
    print(f"  📈 Total Cases Analyzed: {summary_stats['total_cases']:,}")
    print(f"  💀 Total Deaths Analyzed: {summary_stats['total_deaths']:,}")
    print(f"  🏳️ Countries Included: {summary_stats['countries']}")
    print(f"  💔 Global CFR: {summary_stats['global_cfr']:.2f}%")
    print(f"  🎯 Country Clusters Found: {summary_stats['clusters']}")
    print(f"  🎯 Clustering Silhouette Score: {clusterer.silhouette_scores[np.argmax(clusterer.silhouette_scores)]:.3f}")
    print(f"  📈 Forecasting R² (Cases): {forecast_results['cases_r2']:.3f}")
    print(f"  📈 Forecasting R² (Deaths): {forecast_results['deaths_r2']:.3f}")
    print(f"  🚨 Outbreak Prediction Accuracy: {summary_stats['accuracy']:.1f}%")
    print(f"  🚨 Outbreak Prediction F1-Score: {outbreak_results['f1']:.3f}")
    
    print("\n📁 GENERATED FILES:")
    print("  📊 Visualizations saved to: visualizations/")
    print("  💾 Processed data saved to: data/processed/")
    print("  📓 Analysis notebook: notebooks/covid19_comprehensive_analysis.ipynb")
    print("  📋 Documentation: docs/ and README.md")
    print("  🎨 Power BI Guide: powerbi/COVID19_Dashboard_Guide.md")
    
    print("\n✅ All capstone project requirements completed successfully!")
    print("🎓 Ready for presentation and grading!")

if __name__ == "__main__":
    # Create output directories
    os.makedirs('visualizations', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Run the main analysis
    main()