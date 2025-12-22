"""
SmartGrow Crop Recommendation Model - Training Script
------------------------------------------------------
Production model with balanced class weights and enhanced dataset
Predicts 43 Kenyan crops including fruits, vegetables, and staples

Dataset: High_Accuracy_Crop_Data_Enhanced.csv (4820 samples, 43 crops)
Includes: Avocado, Macadamia, Cashew, Sweet Potato, Kale, Irish Potato, Millet

Author: SmartGrow Team
Last Updated: December 22, 2025
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
import pickle
import json
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("BALANCED CROP RECOMMENDATION - MODEL TRAINING")
print("=" * 80)

# Load data
print("\n[1] Loading Dataset...")
df = pd.read_csv('data/processed/High_Accuracy_Crop_Data_Enhanced.csv')
print(f"✓ Loaded {len(df)} samples with {df['label'].nunique()} unique crops")

# Fix duplicate crop names
print("\n[2] Cleaning Crop Names...")
crop_mapping = {
    'maize': 'Maize',
    'beans': 'Beans',
    'tomato': 'Tomato',
    'wheat': 'Wheat',
    'sorghum': 'Sorghum',
    'cassava': 'Cassava',
}

df['label'] = df['label'].replace(crop_mapping)
print(f"✓ Merged duplicate crops")
print(f"  Unique crops: {df['label'].nunique()}")

# Show class distribution
print("\n[3] Class Distribution:")
crop_counts = df['label'].value_counts()
print(f"  Most common: {crop_counts.head(3).to_dict()}")
print(f"  Least common: {crop_counts.tail(3).to_dict()}")

# Feature Engineering
print("\n[4] Feature Engineering...")
df['N_P_ratio'] = df['N'] / (df['P'] + 1)
df['N_K_ratio'] = df['N'] / (df['K'] + 1)
df['P_K_ratio'] = df['P'] / (df['K'] + 1)

# Temperature categories - MUST MATCH TRAINING
df['temp_category'] = pd.cut(df['temperature'], 
                               bins=[0, 20, 30, 50], 
                               labels=['low', 'medium', 'high'])

# Rainfall categories
df['rainfall_category'] = pd.cut(df['rainfall'], 
                                   bins=[0, 100, 200, 5000], 
                                   labels=['low', 'medium', 'high'])

# Encode categories
le_temp = LabelEncoder()
le_rain = LabelEncoder()
df['temp_category_encoded'] = le_temp.fit_transform(df['temp_category'].astype(str))
df['rainfall_category_encoded'] = le_rain.fit_transform(df['rainfall_category'].astype(str))

# One-hot encode soil types
soil_encoded = pd.get_dummies(df['soil_type'], prefix='soil')
df = pd.concat([df, soil_encoded], axis=1)

# Encode labels
le_label = LabelEncoder()
df['label_encoded'] = le_label.fit_transform(df['label'])

print(f"✓ Created features")

# Prepare features
feature_columns = [
    'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'season_duration',
    'N_P_ratio', 'N_K_ratio', 'P_K_ratio',
    'temp_category_encoded', 'rainfall_category_encoded'
] + list(soil_encoded.columns)

X = df[feature_columns]
y = df['label_encoded']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✓ Train: {len(X_train)}, Test: {len(X_test)}")

# Scale features
print("\n[5] Scaling Features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Compute class weights to handle imbalance
print("\n[6] Computing Class Weights for Imbalance...")
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = dict(zip(np.unique(y_train), class_weights))

# Show weight examples
sample_crops = list(le_label.inverse_transform([0, 5, 10]))[:3]
sample_weights = [class_weight_dict.get(i, 1.0) for i in [0, 5, 10]]
print(f"  Sample weights: {dict(zip(sample_crops, sample_weights))}")

# Train Random Forest with class weights
print("\n[7] Training Balanced Random Forest...")
rf = RandomForestClassifier(
    n_estimators=300,          # More trees for stability
    max_depth=25,              # Deeper for complex patterns
    min_samples_split=10,       # Prevent overfitting
    min_samples_leaf=4,        # Smooth predictions
    max_features='sqrt',       # Randomness for generalization
    class_weight=class_weight_dict,  # BALANCE CLASSES!
    random_state=42,
    n_jobs=-1,
    verbose=1
)

rf.fit(X_train_scaled, y_train)
print("✓ Training complete")

# Feature importance
print("\n[8] Feature Importance:")
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

print(feature_importance.head(10).to_string(index=False))

# Calibrate probabilities
print("\n[9] Calibrating Probabilities...")
calibrated_rf = CalibratedClassifierCV(
    rf,
    method='sigmoid',
    cv=3
)
calibrated_rf.fit(X_train_scaled, y_train)
print("✓ Calibration complete")

# Evaluate
print("\n[10] Evaluation:")
y_pred = calibrated_rf.predict(X_test_scaled)
y_proba = calibrated_rf.predict_proba(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
print(f"  Accuracy: {accuracy*100:.2f}%")

# Confidence distribution
max_probas = np.max(y_proba, axis=1)
print(f"  Mean confidence: {np.mean(max_probas)*100:.1f}%")
print(f"  Median confidence: {np.median(max_probas)*100:.1f}%")
print(f"  100% confidence: {np.sum(max_probas >= 0.999)/len(max_probas)*100:.1f}%")
print(f"  >90% confidence: {np.sum(max_probas >= 0.9)/len(max_probas)*100:.1f}%")

# Per-crop accuracy (check if fruits are predicted)
print("\n[11] Per-Crop Performance (sample):")
report = classification_report(y_test, y_pred, target_names=le_label.classes_, output_dict=True, zero_division=0)

# Show performance for different crop types
staples = ['Maize', 'Beans', 'Wheat', 'Sorghum']
fruits = ['watermelon', 'pomegranate', 'mango', 'papaya', 'orange']
vegetables = ['Tomato', 'onions', 'cabbage']

for category, crops in [('Staples', staples), ('Fruits', fruits), ('Vegetables', vegetables)]:
    print(f"\n  {category}:")
    for crop in crops:
        if crop in report:
            f1 = report[crop]['f1-score']
            support = report[crop]['support']
            print(f"    {crop:15s}: F1={f1:.3f} (n={int(support)})")

# Save model artifacts
print("\n[12] Saving Model Artifacts...")
with open('models/trained/crop_recommendation_model.pkl', 'wb') as f:
    pickle.dump(calibrated_rf, f)
print("  ✓ crop_recommendation_model.pkl")

with open('models/trained/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("  ✓ scaler.pkl")

with open('models/trained/label_encoder.pkl', 'wb') as f:
    pickle.dump(le_label, f)
print("  ✓ label_encoder.pkl")

with open('models/trained/feature_names.json', 'w') as f:
    json.dump({'features': feature_columns}, f, indent=2)
print("  ✓ feature_names.json")

with open('models/trained/soil_type_mapping.json', 'w') as f:
    soil_types = df['soil_type'].unique().tolist()
    json.dump({'soil_types': soil_types}, f, indent=2)
print("  ✓ soil_type_mapping.json")

print("\n" + "=" * 80)
print("✓ BALANCED MODEL TRAINING COMPLETE!")
print(f"  Accuracy: {accuracy*100:.2f}%")
print(f"  Mean Confidence: {np.mean(max_probas)*100:.1f}%")
print(f"  Crops: {len(le_label.classes_)}")
print("=" * 80)
