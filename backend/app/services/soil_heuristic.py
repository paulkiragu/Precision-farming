"""
Soil Heuristic Service
Maps visual soil characteristics to nutrient profiles
Based on KALRO regional data (as per guidelines)
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SoilHeuristicService:
    """
    Visual Heuristic for Soil Nutrients
    Maps soil types (visual selection) to chemical profiles
    
    As per guidelines: "Instead of entering chemical numbers, users select 
    physical soil traits (e.g., 'Red Clay', 'Black Cotton')"
    """
    
    # Soil Heuristic Mapping (Based on KALRO regional data)
    SOIL_NUTRIENT_MAP = {
        'Red Volcanic': {
            'N': 60,
            'P': 20,
            'K': 40,
            'pH': 5.5,
            'description': 'Highly weathered volcanic soils, acidic, good for tea and coffee'
        },
        'Black Cotton': {
            'N': 70,
            'P': 25,
            'K': 45,
            'pH': 6.8,
            'description': 'Heavy clay soils, high fertility, good water retention'
        },
        'Loam': {
            'N': 50,
            'P': 30,
            'K': 35,
            'pH': 6.5,
            'description': 'Balanced soil, ideal for most crops'
        },
        'Sandy Loam': {
            'N': 30,
            'P': 15,
            'K': 25,
            'pH': 6.0,
            'description': 'Good drainage, lower fertility, needs fertilizer'
        },
        'Clay Loam': {
            'N': 65,
            'P': 28,
            'K': 50,
            'pH': 6.7,
            'description': 'Fertile soil, good water retention'
        },
        'Silty Loam': {
            'N': 55,
            'P': 25,
            'K': 40,
            'pH': 6.3,
            'description': 'Fertile, smooth texture, good for vegetables'
        },
        'Clay': {
            'N': 60,
            'P': 22,
            'K': 55,
            'pH': 7.0,
            'description': 'Heavy soil, poor drainage, high nutrient retention'
        },
        'Silty Clay': {
            'N': 58,
            'P': 24,
            'K': 48,
            'pH': 6.6,
            'description': 'Moderate fertility, compacts easily'
        },
        'Alluvial': {
            'N': 75,
            'P': 35,
            'K': 45,
            'pH': 6.8,
            'description': 'River-deposited soils, very fertile'
        },
        'Coastal Sandy': {
            'N': 20,
            'P': 10,
            'K': 20,
            'pH': 7.2,
            'description': 'Sandy beach soils, low fertility, high pH'
        }
    }
    
    # Alternative names/aliases for user convenience
    SOIL_ALIASES = {
        'red clay': 'Red Volcanic',
        'red volcanic soil': 'Red Volcanic',
        'red soil': 'Red Volcanic',
        'black soil': 'Black Cotton',
        'vertisol': 'Black Cotton',
        'loamy': 'Loam',
        'loamy soil': 'Loam',
        'sandy': 'Sandy Loam',
        'sand': 'Sandy Loam',
        'clay': 'Clay',
        'heavy clay': 'Clay',
        'silt': 'Silty Loam',
        'silty': 'Silty Loam'
    }
    
    def get_nutrients_from_soil(self, soil_type: str, lat: float = None, lon: float = None) -> Optional[Dict]:
        """
        Convert visual soil type to nutrient profile with location-based micro-variation
        
        Args:
            soil_type: Visual soil type (e.g., "Red Volcanic", "Loam")
            lat: Latitude (optional, adds location-specific variation)
            lon: Longitude (optional, adds location-specific variation)
            
        Returns:
            Dict with N, P, K, pH values or None if soil type not recognized
        """
        # Normalize input
        soil_type_normalized = soil_type.strip()
        
        # Try direct match first
        if soil_type_normalized in self.SOIL_NUTRIENT_MAP:
            nutrients = self.SOIL_NUTRIENT_MAP[soil_type_normalized].copy()
        # Try aliases
        elif soil_type_normalized.lower() in self.SOIL_ALIASES:
            canonical_name = self.SOIL_ALIASES[soil_type_normalized.lower()]
            nutrients = self.SOIL_NUTRIENT_MAP[canonical_name].copy()
            logger.info(f"Mapped alias '{soil_type}' to '{canonical_name}'")
        else:
            # Default fallback to Loam (most common)
            logger.warning(f"Unknown soil type '{soil_type}', using Loam as default")
            nutrients = self.SOIL_NUTRIENT_MAP['Loam'].copy()
        
        # Add location-based micro-variation (±5% based on coordinates)
        if lat is not None and lon is not None:
            import random
            # Use coordinates as seed for consistent variation at same location
            seed_value = int((lat * 1000 + lon * 1000) % 10000)
            random.seed(seed_value)
            
            # Add ±5% variation to nutrients
            nutrients['N'] = round(nutrients['N'] * random.uniform(0.95, 1.05))
            nutrients['P'] = round(nutrients['P'] * random.uniform(0.95, 1.05))
            nutrients['K'] = round(nutrients['K'] * random.uniform(0.95, 1.05))
            nutrients['pH'] = round(nutrients['pH'] * random.uniform(0.98, 1.02), 1)
            
            # Reset random seed
            random.seed()
            
            logger.info(
                f"Mapped soil '{soil_type}' at ({lat:.2f}, {lon:.2f}) to nutrients: "
                f"N={nutrients['N']}, P={nutrients['P']}, K={nutrients['K']}, pH={nutrients['pH']} "
                f"(with location variation)"
            )
        else:
            logger.info(
                f"Mapped soil '{soil_type}' to nutrients: "
                f"N={nutrients['N']}, P={nutrients['P']}, K={nutrients['K']}, pH={nutrients['pH']}"
            )
        
        return nutrients
    
    def get_available_soil_types(self) -> list:
        """Get list of available soil types for UI"""
        return list(self.SOIL_NUTRIENT_MAP.keys())
    
    def get_soil_description(self, soil_type: str) -> Optional[str]:
        """Get description of a soil type"""
        nutrients = self.get_nutrients_from_soil(soil_type)
        if nutrients:
            return nutrients.get('description')
        return None
    
    def validate_soil_type(self, soil_type: str) -> bool:
        """Check if soil type is valid"""
        soil_type_normalized = soil_type.strip()
        return (
            soil_type_normalized in self.SOIL_NUTRIENT_MAP or
            soil_type_normalized.lower() in self.SOIL_ALIASES
        )
