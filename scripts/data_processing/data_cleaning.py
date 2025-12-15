"""
Data Cleaning and Harmonization Script
Purpose: Clean and merge datasets for Kenyan Crop Recommendation System
Author: Data Processing Pipeline
Date: December 15, 2025
"""

import pandas as pd
import numpy as np
import os

print("=" * 80)
print("KENYAN CROP RECOMMENDATION - DATA CLEANING & HARMONIZATION")
print("=" * 80)

# Load datasets
print("\n[1/8] Loading datasets...")
try:
    smartgrow_df = pd.read_csv('combined_smartgrow_dataset.csv')
    crop_rec_df = pd.read_csv('Crop_recommendation_dataset.csv')
    print(f"✓ SmartGrow dataset loaded: {smartgrow_df.shape[0]} rows, {smartgrow_df.shape[1]} columns")
    print(f"✓ Crop Recommendation dataset loaded: {crop_rec_df.shape[0]} rows, {crop_rec_df.shape[1]} columns")
except Exception as e:
    print(f"✗ Error loading datasets: {e}")
    exit(1)

# Display original structures
print("\n[2/8] Original Dataset Structures:")
print("\nSmartGrow Dataset Columns:")
print(smartgrow_df.columns.tolist())
print("\nCrop Recommendation Dataset Columns:")
print(crop_rec_df.columns.tolist())

# Clean SmartGrow Dataset
print("\n[3/8] Cleaning SmartGrow Dataset...")

# Step 1: Remove unnecessary columns
columns_to_remove = ['sample_id', 'region', 'lat', 'lon', 'elevation_m', 'yield_est_t_ha']
print(f"  → Removing columns: {columns_to_remove}")
smartgrow_cleaned = smartgrow_df.drop(columns=columns_to_remove, errors='ignore')

# Step 2: Rename columns to match standard naming
column_mapping = {
    'pH': 'ph',
    'N_mgkg': 'N',
    'P_mgkg': 'P',
    'K_mgkg': 'K',
    'soil_texture': 'soil_type',
    'avg_temp_C': 'temperature',
    'annual_rain_mm': 'rainfall',
    'humidity_pct': 'humidity',
    'season_length_days': 'season_duration',
    'crop_label': 'label'
}
print(f"  → Renaming columns for standardization")
smartgrow_cleaned = smartgrow_cleaned.rename(columns=column_mapping)

# Step 3: Reorder columns to match Crop Recommendation dataset
column_order = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'soil_type', 'season_duration', 'label']
smartgrow_cleaned = smartgrow_cleaned[column_order]

print(f"✓ SmartGrow dataset cleaned: {smartgrow_cleaned.shape[0]} rows, {smartgrow_cleaned.shape[1]} columns")

# Standardize Crop Recommendation Dataset
print("\n[4/8] Processing Crop Recommendation Dataset...")

# Add season_duration column (estimate based on crop type and climate)
# Using domain knowledge: different crops have different growing seasons
def estimate_season_duration(row):
    """Estimate growing season based on crop type and environmental factors"""
    crop = row['label'].lower()
    temp = row['temperature']
    rainfall = row['rainfall']
    
    # Crop-specific season durations (days) based on Kenyan agricultural data
    season_map = {
        'rice': 120 + int(rainfall / 50),  # 120-180 days
        'maize': 90 + int(rainfall / 40),  # 90-150 days
        'wheat': 90 + int(temp / 2),       # 90-120 days
        'beans': 60 + int(temp / 3),       # 60-90 days
        'chickpea': 90 + int(temp / 2),
        'kidneybeans': 70 + int(temp / 2),
        'pigeonpeas': 120 + int(rainfall / 50),
        'mothbeans': 70 + int(temp / 3),
        'mungbean': 60 + int(temp / 3),
        'blackgram': 70 + int(temp / 3),
        'lentil': 90 + int(temp / 2),
        'pomegranate': 180 + int(rainfall / 30),
        'banana': 270 + int(rainfall / 40),
        'mango': 150 + int(rainfall / 30),
        'grapes': 150 + int(temp / 2),
        'watermelon': 80 + int(temp / 3),
        'muskmelon': 80 + int(temp / 3),
        'apple': 150 + int(rainfall / 30),
        'orange': 180 + int(rainfall / 30),
        'papaya': 180 + int(rainfall / 35),
        'coconut': 365,
        'cotton': 150 + int(rainfall / 40),
        'jute': 120 + int(rainfall / 40),
        'coffee': 180 + int(rainfall / 30),
    }
    
    # Get base duration, default to 120 if crop not found
    base_duration = season_map.get(crop, 120)
    
    # Cap between reasonable limits
    return max(60, min(365, base_duration))

print("  → Estimating season_duration for each crop...")
crop_rec_df['season_duration'] = crop_rec_df.apply(estimate_season_duration, axis=1)

# Reorder columns
crop_rec_cleaned = crop_rec_df[column_order]

print(f"✓ Crop Recommendation dataset processed: {crop_rec_cleaned.shape[0]} rows, {crop_rec_cleaned.shape[1]} columns")

# Standardize soil_type categories
print("\n[5/8] Standardizing soil_type categories...")

# Create mapping for soil types
soil_mapping = {
    # SmartGrow variations
    'Loamy': 'Loam',
    'Loam-Sandy': 'Sandy Loam',
    'Silty-Clay': 'Silty Clay',
    'Sandy': 'Sandy Loam',
    'Silty': 'Silty Loam',
    'Clay': 'Clay',
    
    # Crop Recommendation variations (keep as-is mostly)
    'Clay Loam': 'Clay Loam',
    'Loam': 'Loam',
    'Sandy Loam': 'Sandy Loam',
    'Silty Loam': 'Silty Loam',
    'Red Volcanic': 'Red Volcanic',
    'Silty Clay': 'Silty Clay'
}

# Apply mapping to SmartGrow dataset
smartgrow_cleaned['soil_type'] = smartgrow_cleaned['soil_type'].map(
    lambda x: soil_mapping.get(x, x) if pd.notna(x) else x
)

print("  SmartGrow soil types:")
print(f"    {smartgrow_cleaned['soil_type'].value_counts().to_dict()}")
print("\n  Crop Recommendation soil types:")
print(f"    {crop_rec_cleaned['soil_type'].value_counts().to_dict()}")

# Check for missing values
print("\n[6/8] Checking for missing values...")
print("\nSmartGrow dataset:")
smartgrow_missing = smartgrow_cleaned.isnull().sum()
print(smartgrow_missing[smartgrow_missing > 0] if smartgrow_missing.sum() > 0 else "  ✓ No missing values")

print("\nCrop Recommendation dataset:")
crop_rec_missing = crop_rec_cleaned.isnull().sum()
print(crop_rec_missing[crop_rec_missing > 0] if crop_rec_missing.sum() > 0 else "  ✓ No missing values")

# Merge datasets
print("\n[7/8] Merging datasets...")
merged_df = pd.concat([smartgrow_cleaned, crop_rec_cleaned], axis=0, ignore_index=True)
print(f"✓ Merged dataset created: {merged_df.shape[0]} rows, {merged_df.shape[1]} columns")

# Data quality summary
print("\n[8/8] Final Dataset Summary:")
print("=" * 80)
print(f"Total Records: {merged_df.shape[0]}")
print(f"Total Features: {merged_df.shape[1] - 1} (+ 1 target)")
print(f"\nFeature Columns: {[col for col in merged_df.columns if col != 'label']}")
print(f"Target Column: label")
print(f"\nUnique Crops: {merged_df['label'].nunique()}")
print(f"Crop Distribution:")
print(merged_df['label'].value_counts())

print("\nNumerical Features Statistics:")
numerical_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'season_duration']
print(merged_df[numerical_cols].describe())

# Save cleaned datasets
print("\n" + "=" * 80)
print("SAVING CLEANED DATASETS")
print("=" * 80)

# Save individual cleaned datasets
smartgrow_cleaned.to_csv('smartgrow_cleaned.csv', index=False)
print(f"✓ Saved: smartgrow_cleaned.csv ({smartgrow_cleaned.shape[0]} rows)")

crop_rec_cleaned.to_csv('crop_recommendation_cleaned.csv', index=False)
print(f"✓ Saved: crop_recommendation_cleaned.csv ({crop_rec_cleaned.shape[0]} rows)")

# Save merged dataset (as per project guidelines)
merged_df.to_csv('High_Accuracy_Crop_Data.csv', index=False)
print(f"✓ Saved: High_Accuracy_Crop_Data.csv ({merged_df.shape[0]} rows)")

print("\n" + "=" * 80)
print("DATA CLEANING COMPLETED SUCCESSFULLY!")
print("=" * 80)
print("\nFiles created:")
print("  1. smartgrow_cleaned.csv - Cleaned SmartGrow dataset")
print("  2. crop_recommendation_cleaned.csv - Cleaned Crop Recommendation dataset")
print("  3. High_Accuracy_Crop_Data.csv - Final merged dataset for model training")
print("\nNext steps:")
print("  → Use High_Accuracy_Crop_Data.csv for model training")
print("  → All columns aligned with project guidelines")
print("  → Ready for feature engineering and model development")
print("=" * 80)
