"""
Visualization Module for COVID-19 Analysis
This module contains functions for creating various visualizations and charts.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os


class COVIDVisualizer:
    """
    Class for creating COVID-19 analysis visualizations.
    """
    
    def __init__(self, output_dir='../visualizations'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 12
    
    def plot_global_trends(self, daily_data, save=True):
        """
        Create global temporal trends visualization.
        
        Parameters:
        -----------
        daily_data : pd.DataFrame
            Daily aggregated global data
        save : bool
            Whether to save the plot
        
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle('Global COVID-19 Temporal Trends', fontsize=20, fontweight='bold')
        
        # Daily new cases
        axes[0,0].plot(daily_data.index, daily_data['New_cases'], color='blue', alpha=0.7)
        axes[0,0].set_title('Daily New Cases Worldwide', fontsize=14, fontweight='bold')
        axes[0,0].set_ylabel('New Cases')
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Daily new deaths
        axes[0,1].plot(daily_data.index, daily_data['New_deaths'], color='red', alpha=0.7)
        axes[0,1].set_title('Daily New Deaths Worldwide', fontsize=14, fontweight='bold')
        axes[0,1].set_ylabel('New Deaths')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # Cumulative cases
        axes[1,0].plot(daily_data.index, daily_data['Cumulative_cases'], color='green', alpha=0.8)
        axes[1,0].set_title('Cumulative Cases Worldwide', fontsize=14, fontweight='bold')
        axes[1,0].set_ylabel('Cumulative Cases')
        axes[1,0].set_xlabel('Date')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Cumulative deaths
        axes[1,1].plot(daily_data.index, daily_data['Cumulative_deaths'], color='purple', alpha=0.8)
        axes[1,1].set_title('Cumulative Deaths Worldwide', fontsize=14, fontweight='bold')
        axes[1,1].set_ylabel('Cumulative Deaths')
        axes[1,1].set_xlabel('Date')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/global_temporal_trends.png', dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_regional_comparison(self, regional_data, save=True):
        """
        Create interactive regional comparison visualization.
        
        Parameters:
        -----------
        regional_data : pd.DataFrame
            Regional daily data
        save : bool
            Whether to save the plot
        
        Returns:
        --------
        plotly.graph_objects.Figure
            Interactive Plotly figure
        """
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily New Cases by WHO Region', 'Daily New Deaths by WHO Region'),
            vertical_spacing=0.1
        )
        
        regions = regional_data['WHO_region'].unique()
        colors = px.colors.qualitative.Set1
        
        for i, region in enumerate(regions):
            region_data = regional_data[regional_data['WHO_region'] == region]
            
            # Cases
            fig.add_trace(
                go.Scatter(
                    x=region_data['Date_reported'],
                    y=region_data['New_cases'],
                    name=f'{region} (Cases)',
                    line=dict(color=colors[i % len(colors)]),
                    mode='lines'
                ),
                row=1, col=1
            )
            
            # Deaths
            fig.add_trace(
                go.Scatter(
                    x=region_data['Date_reported'],
                    y=region_data['New_deaths'],
                    name=f'{region} (Deaths)',
                    line=dict(color=colors[i % len(colors)], dash='dash'),
                    mode='lines'
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            height=800,
            title_text="COVID-19 Regional Trends Comparison",
            title_x=0.5,
            title_font_size=20
        )
        
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="New Cases", row=1, col=1)
        fig.update_yaxes(title_text="New Deaths", row=2, col=1)
        
        if save:
            fig.write_html(f'{self.output_dir}/regional_trends_interactive.html')
        
        return fig
    
    def plot_top_countries(self, country_data, save=True):
        """
        Create top countries analysis visualization.
        
        Parameters:
        -----------
        country_data : pd.DataFrame
            Country-level summary data
        save : bool
            Whether to save the plot
        
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        fig, axes = plt.subplots(1, 2, figsize=(20, 8))
        
        # Top 15 by cases
        top_15_cases = country_data.nlargest(15, 'Cumulative_cases')
        bars1 = axes[0].barh(range(len(top_15_cases)), top_15_cases['Cumulative_cases'],
                            color=plt.cm.viridis(np.linspace(0, 1, len(top_15_cases))))
        axes[0].set_yticks(range(len(top_15_cases)))
        axes[0].set_yticklabels(top_15_cases['Country'])
        axes[0].set_xlabel('Total Cases')
        axes[0].set_title('Top 15 Countries by Total Cases', fontweight='bold')
        axes[0].grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            axes[0].text(width, bar.get_y() + bar.get_height()/2,
                        f'{width:,.0f}', ha='left', va='center', fontsize=9)
        
        # Top 15 by deaths
        top_15_deaths = country_data.nlargest(15, 'Cumulative_deaths')
        bars2 = axes[1].barh(range(len(top_15_deaths)), top_15_deaths['Cumulative_deaths'],
                            color=plt.cm.plasma(np.linspace(0, 1, len(top_15_deaths))))
        axes[1].set_yticks(range(len(top_15_deaths)))
        axes[1].set_yticklabels(top_15_deaths['Country'])
        axes[1].set_xlabel('Total Deaths')
        axes[1].set_title('Top 15 Countries by Total Deaths', fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            axes[1].text(width, bar.get_y() + bar.get_height()/2,
                        f'{width:,.0f}', ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/top_countries_analysis.png', dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_correlation_matrix(self, df, numerical_vars, save=True):
        """
        Create correlation matrix heatmap.
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataset with numerical variables
        numerical_vars : list
            List of numerical variables to include
        save : bool
            Whether to save the plot
        
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        correlation_matrix = df[numerical_vars].corr()
        
        plt.figure(figsize=(12, 10))
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                   square=True, fmt='.3f', cbar_kws={"shrink": .8})
        plt.title('COVID-19 Variables Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/correlation_matrix.png', dpi=300, bbox_inches='tight')
        
        return plt.gcf()
    
    def plot_clustering_results(self, country_features, save=True):
        """
        Create 3D clustering visualization.
        
        Parameters:
        -----------
        country_features : pd.DataFrame
            Country data with cluster assignments
        save : bool
            Whether to save the plot
        
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        optimal_k = country_features['Cluster'].nunique()
        colors = plt.cm.tab10(np.linspace(0, 1, optimal_k))
        
        for i, cluster_id in enumerate(sorted(country_features['Cluster'].unique())):
            cluster_data = country_features[country_features['Cluster'] == cluster_id]
            ax.scatter(cluster_data['Cumulative_cases'],
                      cluster_data['Cumulative_deaths'],
                      cluster_data['Case_Fatality_Rate'],
                      c=[colors[i]], label=f'Cluster {cluster_id}', alpha=0.7, s=50)
        
        ax.set_xlabel('Cumulative Cases')
        ax.set_ylabel('Cumulative Deaths')
        ax.set_zlabel('Case Fatality Rate')
        ax.set_title('Country Clusters: COVID-19 Response Patterns', fontsize=14, fontweight='bold')
        ax.legend()
        
        if save:
            plt.savefig(f'{self.output_dir}/country_clusters_3d.png', dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_forecasting_results(self, test_dates, y_test, predictions, model_name='Model', save=True):
        """
        Create forecasting results visualization.
        
        Parameters:
        -----------
        test_dates : array-like
            Test period dates
        y_test : array-like
            Actual values
        predictions : array-like
            Predicted values
        model_name : str
            Name of the model for title
        save : bool
            Whether to save the plot
        
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        plt.figure(figsize=(16, 8))
        
        plt.plot(test_dates, y_test, label=f'Actual {model_name}', color='blue', linewidth=2)
        plt.plot(test_dates, predictions, label=f'Predicted {model_name}', color='red', linewidth=2, alpha=0.7)
        
        plt.title(f'COVID-19 {model_name}: Actual vs Predicted', fontsize=14, fontweight='bold')
        plt.ylabel(model_name)
        plt.xlabel('Date')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/forecasting_{model_name.lower()}_results.png', dpi=300, bbox_inches='tight')
        
        return plt.gcf()
    
    def plot_feature_importance(self, feature_names, importance_values, title='Feature Importance', save=True):
        """
        Create feature importance visualization.
        
        Parameters:
        -----------
        feature_names : list
            Names of features
        importance_values : array-like
            Importance scores
        title : str
            Plot title
        save : bool
            Whether to save the plot
        
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        plt.figure(figsize=(12, 8))
        
        # Sort by importance
        sorted_indices = np.argsort(importance_values)[::-1]
        sorted_features = [feature_names[i] for i in sorted_indices]
        sorted_importance = [importance_values[i] for i in sorted_indices]
        
        plt.barh(range(len(sorted_features)), sorted_importance,
                color=plt.cm.viridis(np.linspace(0, 1, len(sorted_features))))
        plt.yticks(range(len(sorted_features)), sorted_features)
        plt.xlabel('Feature Importance')
        plt.title(title, fontsize=14, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, importance in enumerate(sorted_importance):
            plt.text(importance, i, f'{importance:.3f}', va='center', ha='left', fontsize=10)
        
        plt.tight_layout()
        
        if save:
            filename = title.lower().replace(' ', '_')
            plt.savefig(f'{self.output_dir}/{filename}.png', dpi=300, bbox_inches='tight')
        
        return plt.gcf()
    
    def create_dashboard_summary(self, summary_stats, save=True):
        """
        Create a summary dashboard with key metrics.
        
        Parameters:
        -----------
        summary_stats : dict
            Dictionary with key statistics
        save : bool
            Whether to save the plot
        
        Returns:
        --------
        matplotlib.figure.Figure
            The created figure
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('COVID-19 Analysis Dashboard Summary', fontsize=20, fontweight='bold')
        
        # Remove axes for clean look
        for ax in axes.flat:
            ax.axis('off')
        
        # Create metric cards
        metrics = [
            ('Total Cases', summary_stats.get('total_cases', 0), 'green'),
            ('Total Deaths', summary_stats.get('total_deaths', 0), 'red'),
            ('Countries Affected', summary_stats.get('countries', 0), 'blue'),
            ('Global CFR (%)', summary_stats.get('global_cfr', 0), 'orange'),
            ('Clusters Found', summary_stats.get('clusters', 0), 'purple'),
            ('Model Accuracy', summary_stats.get('accuracy', 0), 'teal')
        ]
        
        for i, (metric, value, color) in enumerate(metrics):
            row, col = i // 3, i % 3
            ax = axes[row, col]
            
            # Create metric card
            ax.text(0.5, 0.7, metric, ha='center', va='center', fontsize=16, fontweight='bold')
            ax.text(0.5, 0.3, f'{value:,.0f}' if isinstance(value, (int, float)) else str(value), 
                   ha='center', va='center', fontsize=24, fontweight='bold', color=color)
            
            # Add border
            ax.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=False, edgecolor=color, linewidth=2))
        
        plt.tight_layout()
        
        if save:
            plt.savefig(f'{self.output_dir}/dashboard_summary.png', dpi=300, bbox_inches='tight')
        
        return fig


if __name__ == "__main__":
    print("COVID-19 Visualization Module")
    print("This module provides comprehensive visualization capabilities for COVID-19 analysis.")