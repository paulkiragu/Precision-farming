

import os
import pickle
import json
import logging
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class CropPredictor:
    """ML Model wrapper with Kenya agricultural intelligence"""
    
    def __init__(self, model_dir: str = None):
        if model_dir is None:
            model_dir = os.path.join(os.path.dirname(__file__), '../../../models/trained')
        
        self.model_dir = os.path.abspath(model_dir)
        self._load_artifacts()
    
    def _load_artifacts(self):
        """Load all model artifacts"""
        try:
            # Load model
            with open(os.path.join(self.model_dir, 'crop_recommendation_model.pkl'), 'rb') as f:
                self.model = pickle.load(f)
            
            # Load scaler
            with open(os.path.join(self.model_dir, 'scaler.pkl'), 'rb') as f:
                self.scaler = pickle.load(f)
            
            # Load label encoder
            with open(os.path.join(self.model_dir, 'label_encoder.pkl'), 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            # Load feature names
            with open(os.path.join(self.model_dir, 'feature_names.json'), 'r') as f:
                data = json.load(f)
                self.feature_names = data.get('features', data) if isinstance(data, dict) else data
            
            # Load nutrient requirements
            with open(os.path.join(self.model_dir, 'nutrient_requirements.json'), 'r') as f:
                self.nutrient_requirements = json.load(f)
            
            logger.info(f"✓ Model loaded - {len(self.feature_names)} features, {len(self.label_encoder.classes_)} crops")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def predict(self, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make prediction with regional intelligence"""
        try:
            # Engineer features
            features_df = self._engineer_features(enriched_data)
            features_scaled = self.scaler.transform(features_df)
            
            # Get base prediction
            prediction_proba = self.model.predict_proba(features_scaled)[0]
            
            # Apply regional boost ALWAYS (with stronger multipliers)
            climate_zone = enriched_data.get('metadata', {}).get('climate_zone', '')
            location_name = enriched_data.get('location', {}).get('name', 'Unknown')
            
            # Always apply boost - use location name as fallback
            prediction_proba = self._apply_regional_boost(
                prediction_proba, 
                climate_zone if climate_zone else location_name, 
                location_name
            )
            
            # Get top prediction
            prediction_encoded = np.argmax(prediction_proba)
            predicted_crop = self.label_encoder.inverse_transform([prediction_encoded])[0]
            confidence = float(prediction_proba[prediction_encoded])
            
            # Get top 5 recommendations
            top_5_indices = np.argsort(prediction_proba)[-5:][::-1]
            recommendations = [
                {
                    'crop': self.label_encoder.inverse_transform([idx])[0],
                    'confidence': float(prediction_proba[idx]),
                    'rank': i + 1
                }
                for i, idx in enumerate(top_5_indices)
            ]
            
            # Nutrient analysis
            nutrient_analysis = self._analyze_nutrients(predicted_crop, enriched_data)
            
            # Generate advice
            advice = self._generate_advice(predicted_crop, enriched_data, nutrient_analysis)
            
            # Add confidence warning if needed
            if confidence < 0.30:
                advice.insert(0, f"⚠️ Low confidence ({confidence*100:.1f}%) - consider soil testing for better recommendations")
            elif confidence > 0.70:
                advice.insert(0, f"✅ High confidence ({confidence*100:.1f}%) - excellent conditions for {predicted_crop}")
            
            return {
                'success': True,
                'prediction': predicted_crop,
                'confidence': confidence,
                'recommendations': recommendations,
                'nutrient_analysis': nutrient_analysis,
                'advice': advice,
                'input_data': {
                    'location': enriched_data.get('location'),
                    'soil_type': enriched_data.get('soil_type'),
                    'climate': {
                        'temperature': enriched_data.get('temperature'),
                        'rainfall': enriched_data.get('rainfall'),
                        'humidity': enriched_data.get('humidity')
                    }
                },
                'metadata': enriched_data.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _engineer_features(self, data: Dict) -> pd.DataFrame:
        """Match exact training features"""
        soil_mapping = {
            'Red Volcanic': 'Red Volcanic', 'Black Cotton': 'Black Cotton',
            'Loam': 'Loam', 'Sandy Loam': 'Sandy Loam', 'Clay Loam': 'Clay Loam',
            'Clay': 'Clay', 'Silty Loam': 'Silty Loam', 'Silty Clay': 'Silty Clay',
            'Alluvial': 'Alluvial', 'Coastal Sandy': 'Coastal Sandy', 'Sandy': 'Sand'
        }
        
        soil_type = soil_mapping.get(data.get('soil_type', 'Loam'), data.get('soil_type', 'Loam'))
        
        features = {
            'N': data.get('N', 0),
            'P': data.get('P', 0),
            'K': data.get('K', 0),
            'temperature': data.get('temperature', 0),
            'humidity': data.get('humidity', 0),
            'ph': data.get('pH', data.get('ph', 7.0)),
            'rainfall': data.get('rainfall', 0)
        }
        
        # Soil one-hot
        for soil in ['Alluvial', 'Black Cotton', 'Clay', 'Clay Loam', 'Coastal Sandy',
                     'Loam', 'Red Volcanic', 'Sand', 'Sandy Loam', 'Silty Clay', 'Silty Loam']:
            features[f'soil_{soil}'] = 1 if soil_type == soil else 0
        
        features['season_duration'] = data.get('season_duration', 180)
        
        return pd.DataFrame([features])[self.feature_names]
    
    def _apply_regional_boost(self, proba: np.ndarray, zone: str, location: str) -> np.ndarray:
        """Kenya agricultural intelligence with comprehensive location-specific boosts"""
        boosted = proba.copy()
        crops = self.label_encoder.classes_
        
        zone_lower = zone.lower() if zone else ''
        location_lower = location.lower() if location else ''
        
        logger.info(f"Regional boost - Zone: '{zone}', Location: '{location}'")
        
        #  RICE IRRIGATION
        rice_locations = ['mwea', 'tebere', 'thiba', 'wang\'uru', 'ahero', 'bunyala', 
                         'west kano', 'kano plains', 'mauche']
        # EXACT match for rice scheme zone 
        if 'rice scheme' in zone_lower or any(loc in location_lower for loc in rice_locations):
            boosts = {
                'rice': 100.0, 'maize': 5.0, 'beans': 4.0, 'tomato': 3.0,
                'tea': 0.01, 'coffee': 0.01, 'avocado': 0.02
            }
            logger.info("Applied RICE IRRIGATION SCHEME boost")
        
        #  COASTAL REGIONS 
        elif 'coastal' in zone_lower or any(loc in location_lower for loc in [
            'mombasa', 'malindi', 'lamu', 'kilifi', 'watamu', 'diani', 'kwale', 
            'voi', 'taveta', 'msambweni', 'ukunda', 'gede', 'mambrui'
        ]):
            boosts = {
                'coconut': 18.0, 'cashew': 15.0, 'mango': 12.0, 'cassava': 8.0,
                'papaya': 7.0, 'pineapple': 6.0, 'banana': 5.0,
                'sweet potato': 0.15, 'irish potato': 0.02, 'tea': 0.02, 'coffee': 0.02, 'rice': 0.1
            }
            logger.info("Applied COASTAL boost")
        
        #  PINEAPPLE ZONES (Thika, Murang'a) 
        elif any(loc in location_lower for loc in [
            'thika', 'juja', 'ruiru', 'gatundu', 'githunguri', 'kandara'
        ]):
            boosts = {
                'pineapple': 150.0, 'coffee': 30.0, 'macadamia': 20.0,
                'maize': 15.0, 'beans': 15.0, 'kale': 12.0, 'avocado': 2.0,
                'tea': 0.2, 'coconut': 0.01, 'rice': 0.05
            }
            logger.info("Applied PINEAPPLE ZONE boost")
        
        #MT. KENYA FRUIT ZONE (Embu, Meru lower) 
        elif 'mt. kenya fruit' in zone_lower or 'kenya fruit' in zone_lower or any(loc in location_lower for loc in [
            'kangaru', 'embu', 'siakago', 'runyenjes', 'meru south', 'chuka lower'
        ]):
            boosts = {
                'coffee': 400.0, 'macadamia': 350.0, 'banana': 150.0,
                'beans': 15.0, 'maize': 15.0, 'avocado': 8.0, 'irish potato': 10.0,
                'tea': 0.1, 'coconut': 0.01, 'rice': 0.05, 'cashew': 0.02
            }
            logger.info("Applied MT. KENYA FRUIT ZONE boost")
        
        #  HIGHLAND TEA/COFFEE ZONES (Kericho, Nyeri upper)
        elif any(loc in location_lower for loc in [
            'kericho', 'nandi', 'bomet', 'kapsabet', 'kapsowar', 'sotik', 'nyamira', 
            'keroka', 'kiambu', 'limuru', 'tigoni', 'muranga', 'murang\'a',
            'nyeri', 'karatina', 'meru upper', 'kenol', 'sagana'
        ]):
            boosts = {
                'tea': 50.0, 'coffee': 35.0, 'irish potato': 22.0, 'avocado': 22.0,
                'macadamia': 18.0, 'kale': 16.0, 'cabbage': 12.0, 'beans': 12.0,
                'coconut': 0.01, 'cashew': 0.01, 'mango': 0.1, 'rice': 0.05
            }
            logger.info("Applied HIGHLAND TEA/COFFEE boost")
        
        # RIFT VALLEY 
        elif any(loc in location_lower for loc in [
            'eldoret', 'kitale', 'molo', 'njoro', 'elburgon', 'mau narok', 'burnt forest',
            'lessos', 'turbo', 'soy', 'ziwa', 'timboroa', 'kipkaren'
        ]):
            boosts = {
                'maize': 50.0, 'wheat': 45.0, 'beans': 22.0, 'irish potato': 22.0,
                'barley': 18.0, 'kale': 16.0, 'cabbage': 12.0,
                'tea': 0.15, 'rice': 0.05, 'coconut': 0.01
            }
            logger.info("Applied RIFT VALLEY MAIZE/WHEAT boost")
        
        #  WESTERN HIGH RAINFAll
        elif any(loc in location_lower for loc in [
            'kisumu', 'kakamega', 'bungoma', 'busia', 'mumias', 'webuye', 'malava',
            'butere', 'khwisero', 'siaya', 'yala', 'ugunja', 'vihiga', 'mbale'
        ]):
            boosts = {
                'sugarcane': 50.0, 'maize': 25.0, 'beans': 20.0, 'banana': 20.0,
                'sweet potato': 18.0, 'cassava': 18.0, 'sorghum': 14.0,
                'tea': 0.15, 'coconut': 0.03, 'rice': 0.1
            }
            logger.info("Applied WESTERN HIGH RAINFALL boost")
        
        #  CENTRAL KENYA MIXED FARMING
        elif any(loc in location_lower for loc in [
            'nairobi', 'machakos', 'makueni', 'kitui', 'kangundo', 'wamunyu', 'tala',
            'kathiani', 'mwala', 'matungulu'
        ]):
            boosts = {
                'maize': 18.0, 'beans': 18.0, 'kale': 15.0, 'tomato': 15.0,
                'irish potato': 13.0, 'onion': 11.0, 'cabbage': 11.0,
                'tea': 0.1, 'coconut': 0.03, 'rice': 0.05
            }
            logger.info("Applied CENTRAL MIXED FARMING boost")
        
        #  NYANZA REGION
        elif any(loc in location_lower for loc in [
            'kisii', 'nyamira', 'migori', 'homa bay', 'homabay', 'rongo', 'kehancha',
            'oyugis', 'kendu bay', 'mbita', 'suba'
        ]):
            boosts = {
                'banana': 15.0, 'maize': 10.0, 'beans': 10.0, 'sweet potato': 10.0,
                'sorghum': 8.5, 'finger millet': 8.5, 'avocado': 8.5,
                'tea': 0.15, 'coconut': 0.02, 'rice': 0.1
            }
            logger.info("Applied NYANZA boost")
        
        # ARID/SEMI-ARID (Eastern & Northern)
        elif 'arid' in zone_lower or 'dry' in zone_lower or any(loc in location_lower for loc in [
            'garissa', 'wajir', 'mandera', 'marsabit', 'moyale', 'isiolo', 'meru north',
            'tharaka', 'mwingi', 'kibwezi', 'mtito andei', 'makindu'
        ]):
            boosts = {
                'millet': 18.0, 'sorghum': 18.0, 'cowpeas': 14.0, 'green gram': 14.0,
                'cassava': 11.0, 'pigeon peas': 9.0,
                'tea': 0.02, 'coffee': 0.02, 'irish potato': 0.05, 'rice': 0.05
            }
            logger.info("Applied ARID/SEMI-ARID boost")
        
        # MOUNT KENYA REGION (Fruit Basket)
        elif any(loc in location_lower for loc in [
            'nanyuki', 'laikipia', 'naro moru', 'timau', 'isiolo'
        ]):
            boosts = {
                'wheat': 15.0, 'barley': 12.0, 'irish potato': 15.0, 'beans': 10.0,
                'maize': 8.5, 'avocado': 10.0,
                'tea': 0.15, 'coconut': 0.02, 'rice': 0.05
            }
            logger.info("Applied MOUNT KENYA boost")
        
        #  FALLBACK TO ZONE-BASED 
        elif 'highland mixed' in zone_lower:
            boosts = {
                'maize': 500.0, 'beans': 500.0, 'coffee': 150.0, 'kale': 120.0,
                'cabbage': 80.0, 'irish potato': 80.0, 'avocado': 5.0,
                'tea': 0.2, 'coconut': 0.02, 'rice': 0.05
            }
            logger.info("Applied HIGHLAND MIXED (zone fallback) boost")
        
        elif 'highland' in zone_lower or 'tea' in zone_lower:
            boosts = {
                'tea': 55.0, 'coffee': 40.0, 'irish potato': 30.0, 'avocado': 30.0,
                'macadamia': 25.0, 'kale': 22.0,
                'coconut': 0.02, 'cashew': 0.02, 'rice': 0.05
            }
            logger.info("Applied HIGHLAND (zone fallback) boost")
        
        elif 'western' in zone_lower:
            boosts = {
                'sugarcane': 28.0, 'maize': 20.0, 'beans': 18.0, 'banana': 18.0,
                'tea': 0.08, 'coconut': 0.02
            }
            logger.info("Applied WESTERN (zone fallback) boost")
        
        elif 'central' in zone_lower:
            boosts = {
                'maize': 25.0, 'beans': 25.0, 'irish potato': 18.0, 'kale': 16.0,
                'tea': 0.08, 'rice': 0.05
            }
            logger.info("Applied CENTRAL (zone fallback) boost")
        
        else:
            if any(word in location_lower for word in ['town', 'city', 'urban']):
                boosts = {'kale': 15.0, 'tomato': 15.0, 'cabbage': 13.0, 'onion': 12.0}
                logger.info("Applied URBAN/PERI-URBAN boost")
            else:
                boosts = {}
                logger.info("No regional boost applied - using raw model prediction")
        
        # Apply boosts
        for crop_name, factor in boosts.items():
            idx = np.where(np.char.lower(crops.astype(str)) == crop_name.lower())[0]
            if len(idx) > 0:
                boosted[idx[0]] *= factor
        
        # Normalize to get probabilities
        boosted = boosted / boosted.sum()
        
        return boosted
    
    def _analyze_nutrients(self, crop: str, data: Dict) -> Dict:
        """Nutrient gap analysis"""
        try:
            # Get crop requirements with proper defaults
            crop_lower = crop.lower()
            required = self.nutrient_requirements.get(crop, 
                       self.nutrient_requirements.get(crop_lower, 
                       {'N': 50, 'P': 30, 'K': 30}))
            
            # Extract NPK from data with multiple fallback paths
            soil_data = data.get('soil', {})
            nutrients_data = data.get('nutrients', {})
            
            actual = {
                'N': (data.get('N') or 
                      soil_data.get('N') or 
                      nutrients_data.get('N') or 
                      data.get('n') or 50),
                'P': (data.get('P') or 
                      soil_data.get('P') or 
                      nutrients_data.get('P') or 
                      data.get('p') or 30),
                'K': (data.get('K') or 
                      soil_data.get('K') or 
                      nutrients_data.get('K') or 
                      data.get('k') or 30)
            }
            
            gaps = {k: max(0, required.get(k, 50) - actual.get(k, 0)) for k in ['N', 'P', 'K']}
            total_gap = sum(gaps.values())
            
            status = 'optimal' if total_gap == 0 else 'adequate' if total_gap < 50 else 'deficient'
            
            recommendations = []
            if gaps['N'] > 30: recommendations.append('Apply nitrogen fertilizer (Urea/CAN)')
            if gaps['P'] > 20: recommendations.append('Apply phosphorus fertilizer (DAP/TSP)')
            if gaps['K'] > 20: recommendations.append('Apply potassium fertilizer (MOP/SOP)')
            if not recommendations: recommendations.append('Soil nutrients adequate')
            
            return {
                'status': status,
                'required': required,
                'actual': actual,
                'gaps': gaps,
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Nutrient analysis failed: {e}", exc_info=True)
            return {
                'status': 'unknown', 
                'error': str(e),
                'actual': {'N': 50, 'P': 30, 'K': 30},
                'recommendations': ['Unable to analyze nutrients']
            }
    
    def _generate_advice(self, crop: str, data: Dict, nutrients: Dict) -> List[str]:
        """Agronomic advice"""
        advice = []
        
        rainfall = data.get('rainfall', 0)
        temp = data.get('temperature', 0)
        ph = data.get('pH', data.get('ph', 7.0))
        
        if rainfall < 600:
            advice.append('⚠️ Low rainfall - consider irrigation')
        elif rainfall > 2000:
            advice.append('⚠️ High rainfall - ensure drainage')
        
        if temp > 35:
            advice.append('🌡️ High temp - mulch and water adequately')
        elif temp < 15:
            advice.append('🌡️ Cool temp - use cold-tolerant varieties')
        
        if nutrients.get('status') == 'deficient':
            advice.append('🌱 Soil deficient - apply fertilizers')
        
        if ph < 5.5:
            advice.append('⚗️ Acidic soil - consider liming')
        elif ph > 8.0:
            advice.append('⚗️ Alkaline soil - add organic matter')
        
        if not advice:
            advice.append('✅ Good growing conditions')
        
        return advice
    
    def get_supported_crops(self) -> List[str]:
        return list(self.label_encoder.classes_)
    
    def get_supported_soil_types(self) -> List[str]:
        return ['Alluvial', 'Black Cotton', 'Clay', 'Clay Loam', 'Coastal Sandy',
                'Loam', 'Red Volcanic', 'Sandy Loam', 'Silty Clay', 'Silty Loam']


_predictor_instance = None

def get_predictor() -> CropPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = CropPredictor()
    return _predictor_instance
