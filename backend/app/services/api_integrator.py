
import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime

from .geocoding_service import GeocodingService
from .weather_service import WeatherService
from .soil_heuristic import SoilHeuristicService
from .cache_manager import get_cache
from .kenya_climate_corrector import KenyaClimateCorrector

logger = logging.getLogger(__name__)

class APIIntegrator:
    """
    Master orchestrator for API integration
    Handles parallel API calls, caching, and data combination
    Now includes Kenya-specific climate corrections
    """
    
    def __init__(self):
        self.geocoding = GeocodingService()
        self.weather = WeatherService()
        self.soil_heuristic = SoilHeuristicService()
        self.cache = get_cache()
        self.climate_corrector = KenyaClimateCorrector(geocoding_service=self.geocoding)
    
    async def enrich_user_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method: Enrich user input with API data
        
        Input format:
        {
            "location": "Nakuru" OR {"lat": -0.3031, "lon": 36.0800},
            "soil_type": "Red Volcanic"
        }
        
        Output format:
        {
            "N": 60,
            "P": 20,
            "K": 40,
            "pH": 5.5,
            "temperature": 23.3,
            "humidity": 76,
            "rainfall": 1554,
            "season_duration": 180,
            "soil_type": "Red Volcanic",
            "location": {"lat": -0.3031, "lon": 36.0800, "name": "Nakuru"},
            "metadata": {...}
        }
        
        Args:
            user_input: User-provided data
            
        Returns:
            Enriched data ready for ML model
        """
        try:
            logger.info("Starting data enrichment process...")
            start_time = datetime.utcnow()
            
            # Step 1: Extract and validate input
            location_input = user_input.get('location')
            soil_type = user_input.get('soil_type', 'Loam')
            
            if not location_input:
                raise ValueError("Location is required")
            
            # Step 2: Get coordinates (with caching)
            coordinates = await self._get_coordinates(location_input)
            if not coordinates:
                raise ValueError("Could not determine location coordinates")
            
            # Step 3: Parallel API calls for weather + soil heuristics
            # Pass soil_type to weather service for moisture calculation
            weather_data, soil_nutrients = await self._fetch_parallel_data(
                coordinates['lat'],
                coordinates['lon'],
                soil_type
            )
            
            if not weather_data:
                raise ValueError("Could not fetch weather data")
            
            if not soil_nutrients:
                raise ValueError("Could not map soil type to nutrients")
            
            # Step 3.5: Apply Kenya-specific climate corrections
            location_name = location_input if isinstance(location_input, str) else 'Unknown'
            corrected_climate = await self.climate_corrector.correct_climate_data(
                location_name,
                weather_data['temperature'],
                weather_data['rainfall'],
                weather_data['humidity'],
                lat=coordinates.get('lat'),  # Pass coordinates for geographic detection
                lon=coordinates.get('lon')
            )
            
            logger.info(
                f"Climate correction: Zone={corrected_climate.get('zone', 'Unknown')}, "
                f"Corrected={corrected_climate['corrected']}"
            )
            
            # Use corrected climate data
            temperature = corrected_climate['temperature']
            rainfall = corrected_climate['rainfall']
            humidity = corrected_climate['humidity']
            
            # Step 4: Calculate season duration
            season_duration = self._estimate_season_duration(
                temperature,
                rainfall
            )
            
            # Step 5: Combine all data
            enriched_data = {
                # Soil nutrients (from heuristic)
                'N': soil_nutrients['N'],
                'P': soil_nutrients['P'],
                'K': soil_nutrients['K'],
                'ph': soil_nutrients['pH'],
                
                # Weather data (corrected for Kenya)
                'temperature': temperature,
                'humidity': humidity,
                'rainfall': rainfall,
                
                # Calculated/derived
                'season_duration': season_duration,
                'soil_type': soil_type,
                
                # Location info
                'location': {
                    'lat': coordinates['lat'],
                    'lon': coordinates['lon'],
                    'name': location_input if isinstance(location_input, str) else 'Custom Location'
                },
                
                # Metadata for transparency
                'metadata': {
                    'weather_source': weather_data.get('data_source', 'unknown'),
                    'climate_warning': weather_data.get('climate_warning', False),
                    'climate_deviation': weather_data.get('climate_deviation_factor', 1.0),
                    'climate_corrected': corrected_climate['corrected'],
                    'climate_zone': corrected_climate.get('zone', 'Unknown'),
                    'county': corrected_climate.get('county', ''),  # NEW: County/region information
                    'original_climate': corrected_climate.get('original') if corrected_climate['corrected'] else None,
                    'soil_description': soil_nutrients.get('description', ''),
                    
                    # NEW: Enhanced metadata from multi-source weather
                    'elevation': weather_data.get('elevation'),
                    'microclimate_adjusted': weather_data.get('microclimate_adjusted', False),
                    'historical_blended': weather_data.get('historical_blended', False),
                    'blend_ratio': weather_data.get('blend_ratio'),
                    'evapotranspiration': weather_data.get('evapotranspiration'),
                    'soil_moisture_index': weather_data.get('soil_moisture_index'),
                    'moisture_level': weather_data.get('moisture_level'),
                    'effective_moisture': weather_data.get('effective_moisture'),
                    'climate_indicators': weather_data.get('climate_indicators'),
                    
                    # NEW: Ensemble weather metadata
                    'ensemble_confidence': weather_data.get('ensemble_confidence'),
                    'ensemble_sources': weather_data.get('ensemble_sources'),
                    'ensemble_variance': weather_data.get('ensemble_variance'),
                    
                    'timestamp': datetime.utcnow().isoformat(),
                    'processing_time_ms': int((datetime.utcnow() - start_time).total_seconds() * 1000)
                }
            }
            
            logger.info(f"Data enrichment completed in {enriched_data['metadata']['processing_time_ms']}ms")
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error in data enrichment: {e}")
            raise
    
    async def _get_coordinates(self, location_input: Any) -> Optional[Dict]:
        """
        Get coordinates from location input (with caching)
        Handles both location names and coordinate objects
        """
        # Case 1: Already have coordinates
        if isinstance(location_input, dict):
            lat = location_input.get('lat')
            lon = location_input.get('lon')
            
            if lat is not None and lon is not None:
                # Validate coordinates
                if self.geocoding.validate_coordinates(lat, lon):
                    logger.info(f"Using provided coordinates: ({lat}, {lon})")
                    return {'lat': lat, 'lon': lon}
                else:
                    logger.error(f"Invalid coordinates: ({lat}, {lon})")
                    return None
        
        # Case 2: Location name - need to geocode
        if isinstance(location_input, str):
            location_name = location_input.strip()
            location_lower = location_name.lower()
            
            # Priority 1: Check verified locations database (most accurate)
            if hasattr(self.climate_corrector, 'VERIFIED_LOCATIONS'):
                if location_lower in self.climate_corrector.VERIFIED_LOCATIONS:
                    verified = self.climate_corrector.VERIFIED_LOCATIONS[location_lower]
                    coords = {'lat': verified['lat'], 'lon': verified['lon']}
                    logger.info(f"Using verified coordinates for '{location_name}': ({coords['lat']}, {coords['lon']})")
                    return coords
            
            # Priority 2: Check cache
            cached_coords = self.cache.get_cached_geocoding(location_name)
            if cached_coords:
                logger.info(f"Using cached coordinates for '{location_name}'")
                return cached_coords
            
            # Priority 3: Call geocoding API
            coords = await self.geocoding.get_coordinates(location_name)
            
            # Cache result if successful
            if coords:
                self.cache.cache_geocoding(location_name, coords)
            
            return coords
        
        return None
    
    async def _fetch_parallel_data(
        self,
        lat: float,
        lon: float,
        soil_type: str
    ) -> tuple:
        """
        Fetch weather and soil data in parallel (Option B implementation)
        
        Returns:
            Tuple of (weather_data, soil_nutrients)
        """
        # Check weather cache first
        cached_weather = self.cache.get_cached_weather(lat, lon)
        
        if cached_weather:
            logger.info("Using cached weather data")
            # Soil heuristic with location-based variation
            soil_nutrients = self.soil_heuristic.get_nutrients_from_soil(soil_type, lat, lon)
            return (cached_weather, soil_nutrients)
        
        # Parallel execution
        logger.info("Fetching data in parallel...")
        
        # Create tasks for parallel execution - NOW PASSING SOIL_TYPE
        weather_task = self.weather.get_weather_data(lat, lon, soil_type=soil_type)
        # Soil heuristic with location-based variation
        soil_nutrients = self.soil_heuristic.get_nutrients_from_soil(soil_type, lat, lon)
        
        # Wait for weather API (soil is already done)
        weather_data = await weather_task
        
        # Cache weather data
        if weather_data:
            self.cache.cache_weather(lat, lon, weather_data)
        
        return (weather_data, soil_nutrients)
    
    def _estimate_season_duration(self, temperature: float, rainfall: float) -> int:
        """
        Estimate growing season duration based on climate
        
        Args:
            temperature: Average temperature in Celsius
            rainfall: Annual rainfall in mm
            
        Returns:
            Estimated season duration in days
        """
        # Base season duration
        base_duration = 120
        
        # Adjust for temperature (warmer = faster growth)
        if temperature > 25:
            temp_adjustment = -10
        elif temperature < 18:
            temp_adjustment = +15
        else:
            temp_adjustment = 0
        
        # Adjust for rainfall (more rain = potentially longer season)
        if rainfall > 1500:
            rain_adjustment = +30
        elif rainfall > 1000:
            rain_adjustment = +15
        elif rainfall < 500:
            rain_adjustment = -20
        else:
            rain_adjustment = 0
        
        duration = base_duration + temp_adjustment + rain_adjustment
        
        # Clamp between reasonable values
        return max(60, min(365, duration))
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics"""
        return self.cache.get_stats()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")


# Convenience function for async execution in sync context
def run_enrichment(user_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for enrich_user_input
    Use this in Flask routes
    """
    integrator = APIIntegrator()
    return asyncio.run(integrator.enrich_user_input(user_input))
