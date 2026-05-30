"""
Crop Guidance Service
Provides detailed planting instructions adjusted for local conditions
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class CropGuidanceService:
    """Service for providing crop-specific planting guidance based on conditions"""

    def __init__(self, data_path: str = None):
        if data_path is None:
            data_path = os.path.join(
                os.path.dirname(__file__),
                '../data/crop_guidance.json'
            )

        self.data_path = os.path.abspath(data_path)
        self._load_guidance_data()

    def _load_guidance_data(self):
        """Load crop guidance data from JSON file"""
        try:
            with open(self.data_path, 'r') as f:
                self.guidance_data = json.load(f)
            logger.info(f"Loaded guidance for {len(self.guidance_data)} crops")
        except FileNotFoundError:
            logger.error(f"Guidance data file not found: {self.data_path}")
            self.guidance_data = {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in guidance file: {e}")
            self.guidance_data = {}

    def get_available_crops(self) -> List[str]:
        """Get list of crops with available guidance"""
        return list(self.guidance_data.keys())

    def get_guidance(self, crop: str, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get planting guidance for a crop adjusted for specific conditions

        Args:
            crop: Name of the crop
            conditions: Dictionary with conditions like:
                - rainfall: Annual rainfall in mm
                - temperature: Average temperature in C
                - soil_type: Type of soil
                - humidity: Humidity percentage
                - climate_zone: Climate zone name

        Returns:
            Dictionary with adjusted guidance
        """
        crop_lower = crop.lower().strip()

        # Try to find the crop (handle variations)
        crop_key = self._find_crop_key(crop_lower)

        if not crop_key:
            return {
                'success': False,
                'error': f'No guidance available for {crop}',
                'available_crops': self.get_available_crops()
            }

        base_guidance = self.guidance_data[crop_key].copy()

        # Calculate adjusted planting parameters
        adjusted_planting = self._adjust_planting(
            base_guidance.get('planting', {}),
            conditions
        )

        # Get condition-specific recommendations
        condition_notes = self._generate_condition_notes(conditions, crop_key)

        # Build response
        return {
            'success': True,
            'crop': base_guidance.get('name', crop.title()),
            'planting': adjusted_planting,
            'fertilizers': base_guidance.get('fertilizers', {}),
            'avoid': base_guidance.get('avoid', []),
            'best_practices': base_guidance.get('best_practices', []),
            'condition_notes': condition_notes,
            'conditions_applied': self._get_applied_conditions(conditions)
        }

    def _find_crop_key(self, crop: str) -> Optional[str]:
        """Find the correct key for a crop name"""
        # Direct match
        if crop in self.guidance_data:
            return crop

        # Try lowercase match
        for key in self.guidance_data:
            if key.lower() == crop.lower():
                return key

        # Try partial match
        for key in self.guidance_data:
            if crop in key.lower() or key.lower() in crop:
                return key

        # Handle common variations
        variations = {
            'potato': 'irish potato',
            'potatoes': 'irish potato',
            'irish potatoes': 'irish potato',
            'sukuma': 'kale',
            'sukuma wiki': 'kale',
            'ndengu': 'green gram',
            'green grams': 'green gram',
            'pigeon pea': 'pigeon peas',
            'cowpea': 'cowpeas',
            'sweet potatoes': 'sweet potato',
            'tomatoes': 'tomato',
            'onions': 'onion',
            'cabbages': 'cabbage',
        }

        normalized = variations.get(crop.lower())
        if normalized and normalized in self.guidance_data:
            return normalized

        return None

    def _adjust_planting(
        self,
        planting_config: Dict[str, Any],
        conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust planting parameters based on conditions"""
        if not planting_config:
            return {}

        default = planting_config.get('default', {}).copy()
        adjustments = planting_config.get('adjustments', {})

        applied_adjustments = []
        adjustment_reasons = []

        rainfall = conditions.get('rainfall', 0)
        temperature = conditions.get('temperature', 0)
        soil_type = conditions.get('soil_type', '').lower()
        humidity = conditions.get('humidity', 0)

        # Rainfall adjustments
        if rainfall > 0:
            if rainfall < 600:
                if 'low_rainfall' in adjustments:
                    adj = adjustments['low_rainfall']
                    default.update({k: v for k, v in adj.items() if k != 'note'})
                    if 'note' in adj:
                        adjustment_reasons.append(f"Low rainfall ({rainfall}mm): {adj['note']}")
                    applied_adjustments.append('low_rainfall')
            elif rainfall > 1800:
                if 'high_rainfall' in adjustments:
                    adj = adjustments['high_rainfall']
                    default.update({k: v for k, v in adj.items() if k != 'note'})
                    if 'note' in adj:
                        adjustment_reasons.append(f"High rainfall ({rainfall}mm): {adj['note']}")
                    applied_adjustments.append('high_rainfall')

        # Temperature adjustments
        if temperature > 30:
            if 'high_temperature' in adjustments:
                adj = adjustments['high_temperature']
                default.update({k: v for k, v in adj.items() if k != 'note'})
                if 'note' in adj:
                    adjustment_reasons.append(f"High temperature ({temperature}°C): {adj['note']}")
                applied_adjustments.append('high_temperature')

        # Soil type adjustments
        if soil_type:
            soil_key = None
            if 'sandy' in soil_type:
                soil_key = 'sandy_soil'
            elif 'clay' in soil_type and 'loam' not in soil_type:
                soil_key = 'clay_soil'
            elif 'coastal' in soil_type:
                soil_key = 'coastal_sandy'

            if soil_key and soil_key in adjustments:
                adj = adjustments[soil_key]
                default.update({k: v for k, v in adj.items() if k != 'note'})
                if 'note' in adj:
                    adjustment_reasons.append(f"Soil type ({soil_type}): {adj['note']}")
                applied_adjustments.append(soil_key)

        # Check for steep slope if mentioned in climate zone
        climate_zone = conditions.get('climate_zone', '').lower()
        if 'highland' in climate_zone or 'slope' in climate_zone:
            if 'steep_slope' in adjustments:
                adj = adjustments['steep_slope']
                default.update({k: v for k, v in adj.items() if k != 'note'})
                if 'note' in adj:
                    adjustment_reasons.append(f"Highland/sloped terrain: {adj['note']}")
                applied_adjustments.append('steep_slope')

        return {
            'parameters': default,
            'adjustments_applied': applied_adjustments,
            'adjustment_reasons': adjustment_reasons
        }

    def _generate_condition_notes(
        self,
        conditions: Dict[str, Any],
        crop_key: str
    ) -> List[str]:
        """Generate additional notes based on conditions"""
        notes = []

        rainfall = conditions.get('rainfall', 0)
        temperature = conditions.get('temperature', 0)
        humidity = conditions.get('humidity', 0)
        soil_type = conditions.get('soil_type', '')

        if rainfall > 0 and rainfall < 500:
            notes.append("⚠️ Very low rainfall - consider irrigation or drought-resistant varieties")

        if temperature > 35:
            notes.append("🌡️ High temperatures - provide mulching and adequate watering")

        if humidity > 85:
            notes.append("💧 High humidity - watch for fungal diseases, ensure good air circulation")

        if 'clay' in soil_type.lower() and 'loam' not in soil_type.lower():
            notes.append("🪨 Heavy clay soil - improve drainage and add organic matter")

        if 'sandy' in soil_type.lower():
            notes.append("🏖️ Sandy soil - add organic matter to improve water retention")

        return notes

    def _get_applied_conditions(self, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Return the conditions that were used for adjustments"""
        return {
            'rainfall_mm': conditions.get('rainfall'),
            'temperature_c': conditions.get('temperature'),
            'humidity_pct': conditions.get('humidity'),
            'soil_type': conditions.get('soil_type'),
            'climate_zone': conditions.get('climate_zone')
        }


# Singleton instance
_guidance_instance = None


def get_guidance_service() -> CropGuidanceService:
    """Get singleton instance of CropGuidanceService"""
    global _guidance_instance
    if _guidance_instance is None:
        _guidance_instance = CropGuidanceService()
    return _guidance_instance
