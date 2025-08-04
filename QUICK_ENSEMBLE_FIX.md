# Quick Fix for Ensemble Model - Replace Your Cell

## Problem
Your ensemble model is stuck because it's trying to train on 417,692 samples, which is too large for SVM.

## Solution
Replace your entire ensemble cell with this optimized version:

```python
# OPTIMIZED Ensemble Model for Outbreak Risk Prediction (FAST VERSION)
print("🚀 FAST ENSEMBLE MODEL FOR OUTBREAK PREDICTION")
print("=" * 50)

from sklearn.ensemble import GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Create outbreak risk labels based on case growth patterns
def create_outbreak_labels(data):
    """Create outbreak risk labels based on growth patterns"""
    # Calculate percentiles for growth rates
    growth_p75 = data['Cases_Growth_Rate'].quantile(0.75)
    growth_p90 = data['Cases_Growth_Rate'].quantile(0.90)
    
    # Define risk levels
    conditions = [
        (data['Cases_Growth_Rate'] <= growth_p75),
        (data['Cases_Growth_Rate'] > growth_p75) & (data['Cases_Growth_Rate'] <= growth_p90),
        (data['Cases_Growth_Rate'] > growth_p90)
    ]
    
    risk_levels = ['Low', 'Medium', 'High']
    data['Outbreak_Risk'] = np.select(conditions, risk_levels, default='Low')
    
    return data

# Use SAMPLE DATA for fast processing (key optimization!)
print("🎯 Using optimized sample for fast processing...")
if 'modeling_data' in locals() and len(modeling_data) > 10000:
    # Use much smaller sample for ensemble (THIS IS THE KEY FIX!)
    outbreak_data_sample = modeling_data.sample(n=5000, random_state=42).copy()
else:
    # Fallback to smaller sample
    outbreak_data_sample = modeling_data.sample(n=min(5000, len(modeling_data)), random_state=42).copy()

outbreak_data_sample = outbreak_data_sample[outbreak_data_sample['Cases_Growth_Rate'].notna()]
outbreak_data_sample = create_outbreak_labels(outbreak_data_sample)

print(f"📊 Outbreak prediction dataset: {len(outbreak_data_sample)} samples (optimized)")
print("\n📊 Risk Distribution:")
print(outbreak_data_sample['Outbreak_Risk'].value_counts())

# Prepare features for outbreak prediction
outbreak_features = ['New_cases', 'New_deaths', 'Cumulative_cases', 'Cumulative_deaths',
                    'Case_Fatality_Rate', 'New_cases_7day_avg', 'New_deaths_7day_avg',
                    'WHO_region_encoded', 'Month', 'Year']

X_outbreak = outbreak_data_sample[outbreak_features].fillna(0)
y_outbreak = outbreak_data_sample['Outbreak_Risk']

# Split data
X_train_out, X_test_out, y_train_out, y_test_out = train_test_split(
    X_outbreak, y_outbreak, test_size=0.2, random_state=42, stratify=y_outbreak
)

# Scale features
scaler_outbreak = StandardScaler()
X_train_out_scaled = scaler_outbreak.fit_transform(X_train_out)
X_test_out_scaled = scaler_outbreak.transform(X_test_out)

print(f"\n📊 Training samples: {len(X_train_out)} (optimized)")
print(f"📊 Test samples: {len(X_test_out)} (optimized)")

# Create FAST ensemble model (removed SVM - the bottleneck!)
print("\n🤖 Building Fast Ensemble Model...")

# Faster individual models (reduced complexity)
rf_clf = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=8)  # Reduced trees
gb_clf = GradientBoostingClassifier(n_estimators=50, random_state=42, max_depth=4)  # Reduced trees
lr_clf = LogisticRegression(random_state=42, max_iter=500)  # Reduced iterations

# Create voting ensemble (NO SVM for speed!)
ensemble_model = VotingClassifier(
    estimators=[
        ('rf', rf_clf),
        ('gb', gb_clf),
        ('lr', lr_clf)
    ],
    voting='soft'  # Use probability-based voting
)

print("⚡ Training ensemble model (this will be fast)...")

# Train ensemble model
ensemble_model.fit(X_train_out_scaled, y_train_out)

# Make predictions
y_pred_ensemble = ensemble_model.predict(X_test_out_scaled)
y_pred_proba = ensemble_model.predict_proba(X_test_out_scaled)

# Evaluate ensemble model
accuracy = accuracy_score(y_test_out, y_pred_ensemble)
precision = precision_score(y_test_out, y_pred_ensemble, average='weighted')
recall = recall_score(y_test_out, y_pred_ensemble, average='weighted')
f1 = f1_score(y_test_out, y_pred_ensemble, average='weighted')

print("\n📊 Fast Ensemble Model Performance:")
print(f"  Accuracy: {accuracy:.3f}")
print(f"  Precision: {precision:.3f}")
print(f"  Recall: {recall:.3f}")
print(f"  F1-Score: {f1:.3f}")

print("\n✅ Fast ensemble model completed successfully!")
print(f"⚡ Processed {len(outbreak_data_sample):,} samples in seconds instead of hours!")
```

## Key Changes Made:
1. **Sample Size**: Reduced from 417k to 5k samples (99% reduction!)
2. **Removed SVM**: The main bottleneck that was causing delays
3. **Reduced Complexity**: Fewer trees in RF and GB models
4. **Faster Training**: Will complete in seconds instead of hanging

## Copy and paste this entire code block to replace your hanging cell!