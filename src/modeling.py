"""
Machine Learning Models Module for COVID-19 Analysis
This module contains machine learning models for clustering, forecasting, and classification.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (silhouette_score, mean_squared_error, r2_score,
                           accuracy_score, precision_score, recall_score, f1_score)


class COVIDClustering:
    """
    Country clustering based on COVID-19 response patterns.
    """
    
    def __init__(self, n_clusters=None):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = None
        self.silhouette_scores = []
        
    def find_optimal_clusters(self, X, k_range=range(2, 11)):
        """
        Find optimal number of clusters using silhouette analysis.
        
        Parameters:
        -----------
        X : array-like
            Feature matrix
        k_range : range
            Range of k values to test
        
        Returns:
        --------
        int
            Optimal number of clusters
        """
        X_scaled = self.scaler.fit_transform(X)
        
        self.silhouette_scores = []
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X_scaled)
            score = silhouette_score(X_scaled, labels)
            self.silhouette_scores.append(score)
        
        optimal_k = k_range[np.argmax(self.silhouette_scores)]
        self.n_clusters = optimal_k
        
        print(f"🎯 Optimal number of clusters: {optimal_k}")
        print(f"📊 Best silhouette score: {max(self.silhouette_scores):.3f}")
        
        return optimal_k
    
    def fit_predict(self, X):
        """
        Fit clustering model and predict clusters.
        
        Parameters:
        -----------
        X : array-like
            Feature matrix
        
        Returns:
        --------
        array
            Cluster labels
        """
        if self.n_clusters is None:
            self.find_optimal_clusters(X)
        
        X_scaled = self.scaler.fit_transform(X)
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        labels = self.kmeans.fit_predict(X_scaled)
        
        print(f"✅ Clustering completed with {self.n_clusters} clusters")
        return labels


class COVIDForecaster:
    """
    Time series forecasting for COVID-19 cases and deaths.
    """
    
    def __init__(self):
        self.cases_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        self.deaths_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
        self.feature_cols = None
        
    def create_time_features(self, df, date_col='Date_reported'):
        """
        Create time-based features for forecasting.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Time series data
        date_col : str
            Name of date column
        
        Returns:
        --------
        pd.DataFrame
            Data with time features
        """
        df_features = df.copy()
        
        # Basic time features
        df_features['day_of_year'] = df_features[date_col].dt.dayofyear
        df_features['month'] = df_features[date_col].dt.month
        df_features['quarter'] = df_features[date_col].dt.quarter
        df_features['year'] = df_features[date_col].dt.year
        df_features['days_since_start'] = (df_features[date_col] - df_features[date_col].min()).dt.days
        
        # Lag features
        df_features['cases_lag_7'] = df_features['New_cases'].shift(7)
        df_features['cases_lag_14'] = df_features['New_cases'].shift(14)
        df_features['deaths_lag_7'] = df_features['New_deaths'].shift(7)
        df_features['deaths_lag_14'] = df_features['New_deaths'].shift(14)
        
        # Rolling averages
        df_features['cases_rolling_7'] = df_features['New_cases'].rolling(7).mean()
        df_features['cases_rolling_14'] = df_features['New_cases'].rolling(14).mean()
        df_features['deaths_rolling_7'] = df_features['New_deaths'].rolling(7).mean()
        df_features['deaths_rolling_14'] = df_features['New_deaths'].rolling(14).mean()
        
        return df_features
    
    def train(self, ts_data, test_size=0.2):
        """
        Train forecasting models.
        
        Parameters:
        -----------
        ts_data : pd.DataFrame
            Time series data with features
        test_size : float
            Proportion of data for testing
        
        Returns:
        --------
        dict
            Training results and metrics
        """
        # Prepare features
        self.feature_cols = ['day_of_year', 'month', 'quarter', 'year', 'days_since_start',
                           'cases_lag_7', 'cases_lag_14', 'deaths_lag_7', 'deaths_lag_14',
                           'cases_rolling_7', 'cases_rolling_14', 'deaths_rolling_7', 'deaths_rolling_14']
        
        X = ts_data[self.feature_cols].dropna()
        y_cases = ts_data.loc[X.index, 'New_cases']
        y_deaths = ts_data.loc[X.index, 'New_deaths']
        
        # Train-test split
        split_idx = int((1 - test_size) * len(X))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_cases_train, y_cases_test = y_cases[:split_idx], y_cases[split_idx:]
        y_deaths_train, y_deaths_test = y_deaths[:split_idx], y_deaths[split_idx:]
        
        # Train models
        self.cases_model.fit(X_train, y_cases_train)
        self.deaths_model.fit(X_train, y_deaths_train)
        
        # Make predictions
        cases_pred = self.cases_model.predict(X_test)
        deaths_pred = self.deaths_model.predict(X_test)
        
        # Calculate metrics
        results = {
            'cases_rmse': np.sqrt(mean_squared_error(y_cases_test, cases_pred)),
            'cases_r2': r2_score(y_cases_test, cases_pred),
            'deaths_rmse': np.sqrt(mean_squared_error(y_deaths_test, deaths_pred)),
            'deaths_r2': r2_score(y_deaths_test, deaths_pred),
            'test_data': {
                'y_cases_test': y_cases_test,
                'y_deaths_test': y_deaths_test,
                'cases_pred': cases_pred,
                'deaths_pred': deaths_pred
            }
        }
        
        print("📊 Forecasting Model Performance:")
        print(f"  Cases - RMSE: {results['cases_rmse']:,.0f}, R²: {results['cases_r2']:.3f}")
        print(f"  Deaths - RMSE: {results['deaths_rmse']:,.0f}, R²: {results['deaths_r2']:.3f}")
        
        return results


class OutbreakPredictor:
    """
    Ensemble model for predicting outbreak risk levels.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.ensemble_model = None
        self.feature_cols = None
        
    def create_risk_labels(self, data, growth_col='Cases_Growth_Rate'):
        """
        Create outbreak risk labels based on growth patterns.
        
        Parameters:
        -----------
        data : pd.DataFrame
            Dataset with growth rate column
        growth_col : str
            Name of growth rate column
        
        Returns:
        --------
        pd.DataFrame
            Data with risk labels
        """
        df_risk = data.copy()
        
        # Calculate percentiles
        growth_p75 = df_risk[growth_col].quantile(0.75)
        growth_p90 = df_risk[growth_col].quantile(0.90)
        
        # Define risk levels
        conditions = [
            (df_risk[growth_col] <= growth_p75),
            (df_risk[growth_col] > growth_p75) & (df_risk[growth_col] <= growth_p90),
            (df_risk[growth_col] > growth_p90)
        ]
        
        risk_levels = ['Low', 'Medium', 'High']
        df_risk['Outbreak_Risk'] = np.select(conditions, risk_levels, default='Low')
        
        return df_risk
    
    def train(self, X, y, test_size=0.2):
        """
        Train ensemble outbreak prediction model.
        
        Parameters:
        -----------
        X : pd.DataFrame
            Features
        y : pd.Series
            Risk labels
        test_size : float
            Proportion of data for testing
        
        Returns:
        --------
        dict
            Training results and metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create ensemble model
        rf_clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        gb_clf = GradientBoostingClassifier(n_estimators=100, random_state=42, max_depth=5)
        svm_clf = SVC(probability=True, random_state=42, C=1.0)
        lr_clf = LogisticRegression(random_state=42, max_iter=1000)
        
        self.ensemble_model = VotingClassifier(
            estimators=[
                ('rf', rf_clf),
                ('gb', gb_clf),
                ('svm', svm_clf),
                ('lr', lr_clf)
            ],
            voting='soft'
        )
        
        # Train model
        self.ensemble_model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = self.ensemble_model.predict(X_test_scaled)
        
        # Calculate metrics
        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1': f1_score(y_test, y_pred, average='weighted'),
            'test_data': {
                'y_test': y_test,
                'y_pred': y_pred
            }
        }
        
        print("📊 Outbreak Prediction Model Performance:")
        print(f"  Accuracy: {results['accuracy']:.3f}")
        print(f"  Precision: {results['precision']:.3f}")
        print(f"  Recall: {results['recall']:.3f}")
        print(f"  F1-Score: {results['f1']:.3f}")
        
        return results


if __name__ == "__main__":
    print("COVID-19 Machine Learning Models Module")
    print("This module provides clustering, forecasting, and classification models.")