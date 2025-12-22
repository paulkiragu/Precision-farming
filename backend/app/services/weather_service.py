"""
Weather Service - Enhanced Multi-Source Weather Integration
Fetches real-time weather data from multiple sources with intelligent fallback
Includes historical patterns, micro-climate detection, and soil moisture calculation
"""

import aiohttp
import logging
import os
from typing import Optional, Dict, List
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Enhanced weather service with multiple data sources and intelligent blending
    
    Data Sources (Priority Order):
    1. Open-Meteo API (primary - free, reliable)
    2. OpenWeatherMap API (secondary - requires API key)
    3. Historical averages + Kenya climate patterns (fallback)
    """
    
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
    OPEN_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
    ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"
    
    # Enhanced Monthly Historical Averages for Kenya (based on climate data)
    # Format: {month: {region: {temp, humidity, rainfall}}}
    MONTHLY_PATTERNS = {
        # Jan-Feb: Hot & Dry
        1: {
            'coastal': {'temp': 30, 'humidity': 75, 'rainfall': 40},
            'highland': {'temp': 20, 'humidity': 60, 'rainfall': 50},
            'western': {'temp': 25, 'humidity': 70, 'rainfall': 80},
            'default': {'temp': 25, 'humidity': 65, 'rainfall': 50}
        },
        2: {
            'coastal': {'temp': 31, 'humidity': 75, 'rainfall': 35},
            'highland': {'temp': 21, 'humidity': 58, 'rainfall': 45},
            'western': {'temp': 26, 'humidity': 68, 'rainfall': 75},
            'default': {'temp': 26, 'humidity': 64, 'rainfall': 45}
        },
        # Mar-May: Long Rains
        3: {
            'coastal': {'temp': 30, 'humidity': 80, 'rainfall': 120},
            'highland': {'temp': 19, 'humidity': 70, 'rainfall': 150},
            'western': {'temp': 25, 'humidity': 78, 'rainfall': 180},
            'default': {'temp': 25, 'humidity': 75, 'rainfall': 140}
        },
        4: {
            'coastal': {'temp': 29, 'humidity': 82, 'rainfall': 200},
            'highland': {'temp': 18, 'humidity': 75, 'rainfall': 220},
            'western': {'temp': 24, 'humidity': 82, 'rainfall': 250},
            'default': {'temp': 24, 'humidity': 78, 'rainfall': 210}
        },
        5: {
            'coastal': {'temp': 28, 'humidity': 80, 'rainfall': 180},
            'highland': {'temp': 17, 'humidity': 72, 'rainfall': 200},
            'western': {'temp': 23, 'humidity': 80, 'rainfall': 220},
            'default': {'temp': 23, 'humidity': 76, 'rainfall': 190}
        },
        # Jun-Aug: Cool & Dry
        6: {
            'coastal': {'temp': 27, 'humidity': 75, 'rainfall': 70},
            'highland': {'temp': 16, 'humidity': 65, 'rainfall': 60},
            'western': {'temp': 22, 'humidity': 72, 'rainfall': 100},
            'default': {'temp': 22, 'humidity': 70, 'rainfall': 70}
        },
        7: {
            'coastal': {'temp': 26, 'humidity': 73, 'rainfall': 60},
            'highland': {'temp': 15, 'humidity': 62, 'rainfall': 50},
            'western': {'temp': 21, 'humidity': 70, 'rainfall': 90},
            'default': {'temp': 21, 'humidity': 68, 'rainfall': 60}
        },
        8: {
            'coastal': {'temp': 26, 'humidity': 73, 'rainfall': 55},
            'highland': {'temp': 16, 'humidity': 60, 'rainfall': 50},
            'western': {'temp': 22, 'humidity': 68, 'rainfall': 95},
            'default': {'temp': 21, 'humidity': 67, 'rainfall': 60}
        },
        # Sep: Transition
        9: {
            'coastal': {'temp': 27, 'humidity': 74, 'rainfall': 65},
            'highland': {'temp': 17, 'humidity': 62, 'rainfall': 55},
            'western': {'temp': 23, 'humidity': 70, 'rainfall': 100},
            'default': {'temp': 22, 'humidity': 68, 'rainfall': 70}
        },
        # Oct-Dec: Short Rains
        10: {
            'coastal': {'temp': 28, 'humidity': 78, 'rainfall': 110},
            'highland': {'temp': 18, 'humidity': 68, 'rainfall': 130},
            'western': {'temp': 24, 'humidity': 75, 'rainfall': 150},
            'default': {'temp': 23, 'humidity': 72, 'rainfall': 120}
        },
        11: {
            'coastal': {'temp': 29, 'humidity': 80, 'rainfall': 150},
            'highland': {'temp': 19, 'humidity': 72, 'rainfall': 180},
            'western': {'temp': 24, 'humidity': 78, 'rainfall': 200},
            'default': {'temp': 24, 'humidity': 75, 'rainfall': 160}
        },
        12: {
            'coastal': {'temp': 30, 'humidity': 78, 'rainfall': 90},
            'highland': {'temp': 20, 'humidity': 68, 'rainfall': 100},
            'western': {'temp': 25, 'humidity': 75, 'rainfall': 130},
            'default': {'temp': 25, 'humidity': 72, 'rainfall': 100}
        }
    }
    
    # Soil water retention rates (field capacity %)
    SOIL_RETENTION = {
        'Clay': 0.45,           # Holds 45% water
        'Clay Loam': 0.38,
        'Loam': 0.32,
        'Sandy Loam': 0.22,
        'Sandy': 0.12,          # Holds 12% water
        'Red Volcanic': 0.35,   # Good retention
        'Black Cotton': 0.42,   # High retention
        'Alluvial': 0.30,
        'Laterite': 0.25,
        'Peat': 0.50           # Excellent retention
    }
    
    def __init__(self):
        """Initialize weather service with API keys"""
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY', '')
        logger.info(f"Weather service initialized. OpenWeather API: {'configured' if self.openweather_api_key else 'not configured'}")
    
    async def get_weather_data(
        self, 
        lat: float, 
        lon: float,
        soil_type: Optional[str] = 'Loam',
        include_forecast: bool = True
    ) -> Optional[Dict]:
        """
        Fetch weather data with multi-source fallback and enhancements
        
        Args:
            lat: Latitude
            lon: Longitude
            soil_type: Soil type for moisture calculation
            include_forecast: Whether to include 14-day forecast
            
        Returns:
            Enhanced weather dict with micro-climate, soil moisture, historical blending
        """
        try:
            # Step 1: Get elevation for micro-climate adjustment
            elevation = await self._get_elevation(lat, lon)
            
            # Step 2: Fetch from MULTIPLE sources for ensemble approach
            weather_sources = []
            
            # Try Open-Meteo (primary)
            open_meteo_data = await self._fetch_open_meteo(lat, lon, include_forecast)
            if open_meteo_data:
                weather_sources.append({
                    'source': 'Open-Meteo',
                    'data': open_meteo_data,
                    'reliability': 0.85  # High reliability
                })
            
            # Try OpenWeatherMap (secondary) if configured
            if self.openweather_api_key:
                openweather_data = await self._fetch_openweathermap(lat, lon)
                if openweather_data:
                    weather_sources.append({
                        'source': 'OpenWeatherMap',
                        'data': openweather_data,
                        'reliability': 0.80  # Good reliability
                    })
            
            # Add historical patterns as baseline
            historical_data = self._get_historical_fallback(lat)
            weather_sources.append({
                'source': 'Historical',
                'data': historical_data,
                'reliability': 0.70  # Moderate reliability
            })
            
            # Step 3: Ensemble aggregation - combine multiple sources intelligently
            if len(weather_sources) > 1:
                weather_data = self._ensemble_aggregate(weather_sources, lat)
                logger.info(f"Ensemble weather from {len(weather_sources)} sources: {[s['source'] for s in weather_sources]}")
            elif len(weather_sources) == 1:
                weather_data = weather_sources[0]['data']
                logger.info(f"Single source weather: {weather_sources[0]['source']}")
            else:
                logger.warning("All sources failed, using default historical fallback")
                weather_data = self._get_historical_fallback(lat)
            
            # Step 4: Apply micro-climate corrections (elevation-based)
            if elevation:
                weather_data = self._apply_microclimate_adjustment(weather_data, elevation)
            
            # Step 5: Blend with historical patterns (40% historical, 60% current)
            weather_data = self._blend_with_historical(weather_data, lat)
            
            # Step 6: Calculate soil moisture and evapotranspiration
            weather_data = self._calculate_soil_moisture(weather_data, soil_type)
            
            # Step 7: Add climate change indicators
            weather_data = self._add_climate_indicators(weather_data, lat)
            
            logger.info(
                f"Enhanced weather data: {weather_data['temperature']:.1f}°C, "
                f"{weather_data['rainfall']:.0f}mm, "
                f"Soil moisture: {weather_data.get('soil_moisture_index', 0):.2f}"
            )
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Critical weather error: {e}")
            return self._get_historical_fallback(lat)
    
    async def _fetch_open_meteo(
        self,
        lat: float,
        lon: float,
        include_forecast: bool = True
    ) -> Optional[Dict]:
        """Fetch from Open-Meteo API (primary source)"""
    async def _fetch_open_meteo(
        self,
        lat: float,
        lon: float,
        include_forecast: bool = True
    ) -> Optional[Dict]:
        """Fetch from Open-Meteo API (primary source)"""
        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': [
                    'temperature_2m',
                    'relative_humidity_2m',
                    'precipitation'
                ],
                'timezone': 'Africa/Nairobi'
            }
            
            # Add forecast parameters if requested
            if include_forecast:
                params['daily'] = [
                    'temperature_2m_max',
                    'temperature_2m_min',
                    'precipitation_sum',
                    'relative_humidity_2m_max'
                ]
                params['forecast_days'] = 14
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.OPEN_METEO_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Extract and process data
                    weather_data = self._process_open_meteo_data(data, lat)
                    weather_data['data_source'] = 'Open-Meteo API'
                    
                    logger.info(f"Open-Meteo data fetched for ({lat:.4f}, {lon:.4f})")
                    return weather_data
                    
        except Exception as e:
            logger.error(f"Open-Meteo API error: {e}")
            return None
    
    async def _fetch_openweathermap(
        self,
        lat: float,
        lon: float
    ) -> Optional[Dict]:
        """Fetch from OpenWeatherMap API (secondary source)"""
        if not self.openweather_api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return None
        
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_api_key,
                'units': 'metric'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.OPEN_WEATHER_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Process OpenWeatherMap data
                    weather_data = {
                        'temperature': data['main']['temp'],
                        'humidity': data['main']['humidity'],
                        'rainfall': self._estimate_annual_rainfall(lat),
                        'data_source': 'OpenWeatherMap API',
                        'current_conditions': data['weather'][0]['description']
                    }
                    
                    logger.info(f"OpenWeatherMap data fetched for ({lat:.4f}, {lon:.4f})")
                    return weather_data
                    
        except Exception as e:
            logger.error(f"OpenWeatherMap API error: {e}")
            return None
    
    async def _get_elevation(self, lat: float, lon: float) -> Optional[float]:
        """Get elevation data for micro-climate adjustment"""
        try:
            params = {
                'latitude': lat,
                'longitude': lon
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.ELEVATION_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    elevation = data.get('elevation', [0])[0]
                    logger.info(f"Elevation: {elevation}m")
                    return elevation
                    
        except Exception as e:
            logger.warning(f"Elevation fetch failed: {e}")
            return None
    
    def _process_open_meteo_data(self, data: Dict, lat: float) -> Dict:
        """Process raw Open-Meteo API data into usable format"""
        current = data.get('current', {})
        daily = data.get('daily', {})
        
        # Current conditions
        temperature = current.get('temperature_2m', 23.0)
        humidity = current.get('relative_humidity_2m', 65.0)
        current_precip = current.get('precipitation', 0.0)
        
        # Calculate 14-day forecast rainfall (for season prediction)
        forecast_rainfall = 0
        if daily and 'precipitation_sum' in daily:
            forecast_rainfall = sum(daily['precipitation_sum'][:14])
        
        # Estimate annual rainfall from 14-day forecast (crude approximation)
        # 14 days → annual: multiply by ~26 (52 weeks / 2)
        estimated_annual_rainfall = forecast_rainfall * 26
        
        # Climate Deviation Detection (Guidelines requirement)
        historical_data = self._get_historical_fallback(lat)
        deviation_factor = self._calculate_climate_deviation(
            estimated_annual_rainfall,
            historical_data['rainfall']
        )
        
        # Adjust rainfall if significant deviation detected
        adjusted_rainfall = estimated_annual_rainfall
        if deviation_factor < 0.5:  # Less than 50% of historical
            logger.warning(
                f"Climate deviation detected: {deviation_factor*100:.1f}% of historical average"
            )
            # Use the lower forecast value to recommend drought-resistant crops
            adjusted_rainfall = estimated_annual_rainfall
        
        return {
            'temperature': round(temperature, 1),
            'humidity': round(humidity, 1),
            'rainfall': round(adjusted_rainfall, 1),
            'current_precipitation': round(current_precip, 1),
            'forecast_14day_total': round(forecast_rainfall, 1),
            'climate_deviation_factor': round(deviation_factor, 2),
            'climate_warning': deviation_factor < 0.5,
            'data_source': 'open-meteo',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_historical_fallback(self, lat: float) -> Dict:
        """Return fallback data based on monthly historical patterns"""
        current_month = datetime.utcnow().month
        region = self._classify_region(lat)
        
        # Get monthly pattern for current month and region
        monthly_data = self.MONTHLY_PATTERNS.get(current_month, {}).get(region, {})
        if not monthly_data:
            monthly_data = self.MONTHLY_PATTERNS.get(current_month, {}).get('default', {
                'temp': 23, 'humidity': 65, 'rainfall': 100
            })
        
        # Estimate annual rainfall (sum all months for this region)
        annual_rainfall = sum(
            self.MONTHLY_PATTERNS.get(month, {}).get(region, {'rainfall': 100})['rainfall']
            for month in range(1, 13)
        )
        
        logger.warning(f"Using historical fallback for {region} region, month {current_month}")
        
        return {
            'temperature': monthly_data['temp'],
            'humidity': monthly_data['humidity'],
            'rainfall': annual_rainfall,
            'current_precipitation': monthly_data['rainfall'] / 30,  # Daily avg
            'forecast_14day_total': monthly_data['rainfall'] / 2,  # Half-month
            'climate_deviation_factor': 1.0,
            'climate_warning': False,
            'data_source': 'historical-fallback',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _classify_region(self, lat: float) -> str:
        """Classify region based on latitude"""
        if lat < -3.5:  # Coastal
            return 'coastal'
        elif lat > 0.5:  # Western
            return 'western'
        elif -1.5 <= lat <= 0.5:  # Highland
            return 'highland'
        else:
            return 'default'
    
    def _ensemble_aggregate(self, weather_sources: list, lat: float) -> Dict:
        """
        Intelligent ensemble aggregation of multiple weather sources
        
        Uses weighted averaging based on source reliability and data quality.
        Outlier detection removes extreme values that differ significantly from median.
        
        Args:
            weather_sources: List of dicts with 'source', 'data', 'reliability'
            lat: Latitude for context
            
        Returns:
            Aggregated weather data with ensemble metadata
        """
        import statistics
        
        # Collect values from all sources
        temps = []
        humidities = []
        rainfalls = []
        weights = []
        sources_used = []
        
        for source in weather_sources:
            data = source['data']
            reliability = source['reliability']
            
            temps.append((data['temperature'], reliability))
            humidities.append((data['humidity'], reliability))
            rainfalls.append((data['rainfall'], reliability))
            weights.append(reliability)
            sources_used.append(source['source'])
        
        # Outlier detection - remove extreme values
        def remove_outliers(values_with_weights):
            """Remove values that are >2 standard deviations from median"""
            if len(values_with_weights) < 2:
                return values_with_weights
            
            values = [v[0] for v in values_with_weights]
            median = statistics.median(values)
            
            if len(values) >= 3:
                stdev = statistics.stdev(values)
                filtered = [(v, w) for v, w in values_with_weights 
                           if abs(v - median) <= 2 * stdev]
                
                if filtered:  # If we have data left after filtering
                    removed = len(values_with_weights) - len(filtered)
                    if removed > 0:
                        logger.info(f"Removed {removed} outlier(s) from ensemble")
                    return filtered
            
            return values_with_weights
        
        # Remove outliers
        temps = remove_outliers(temps)
        humidities = remove_outliers(humidities)
        rainfalls = remove_outliers(rainfalls)
        
        # Weighted average calculation
        def weighted_avg(values_with_weights):
            """Calculate weighted average"""
            total_weight = sum(w for _, w in values_with_weights)
            if total_weight == 0:
                return statistics.mean([v for v, _ in values_with_weights])
            return sum(v * w for v, w in values_with_weights) / total_weight
        
        # Calculate ensemble values
        ensemble_temp = weighted_avg(temps)
        ensemble_humidity = weighted_avg(humidities)
        ensemble_rainfall = weighted_avg(rainfalls)
        
        # Calculate confidence metrics
        temp_variance = statistics.variance([v for v, _ in temps]) if len(temps) > 1 else 0
        rain_variance = statistics.variance([v for v, _ in rainfalls]) if len(rainfalls) > 1 else 0
        
        # High variance means sources disagree - lower confidence
        confidence = 1.0 - min(0.3, (temp_variance / 100 + rain_variance / 10000) / 2)
        
        logger.info(
            f"Ensemble: Temp={ensemble_temp:.1f}°C (σ²={temp_variance:.2f}), "
            f"Rain={ensemble_rainfall:.0f}mm (σ²={rain_variance:.0f}), "
            f"Confidence={confidence:.2%}"
        )
        
        return {
            'temperature': round(ensemble_temp, 1),
            'humidity': round(ensemble_humidity, 1),
            'rainfall': round(ensemble_rainfall, 1),
            'current_precipitation': 0,  # Will be recalculated
            'forecast_14day_total': 0,  # Will be recalculated
            'climate_deviation_factor': 1.0,
            'climate_warning': False,
            'data_source': f'ensemble ({", ".join(sources_used)})',
            'ensemble_confidence': confidence,
            'ensemble_sources': len(weather_sources),
            'ensemble_variance': {
                'temperature': round(temp_variance, 2),
                'rainfall': round(rain_variance, 0)
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _apply_microclimate_adjustment(self, weather_data: Dict, elevation: float) -> Dict:
        """
        Apply micro-climate adjustments based on elevation
        
        Temperature decreases ~6.5°C per 1000m elevation (environmental lapse rate)
        Humidity increases with elevation (orographic effect)
        Rainfall increases on windward slopes
        """
        # Temperature adjustment: -6.5°C per 1000m above sea level
        elevation_km = elevation / 1000.0
        temp_adjustment = -6.5 * elevation_km
        
        # Humidity increases with elevation (up to a point)
        humidity_adjustment = min(10, elevation_km * 5)  # Max +10%
        
        # Rainfall adjustment for highland regions (orographic precipitation)
        rainfall_multiplier = 1.0
        if elevation > 1500:  # Highland areas
            rainfall_multiplier = 1.2  # 20% more rain
        elif elevation > 2500:  # Very high areas
            rainfall_multiplier = 1.4  # 40% more rain
        
        adjusted_data = weather_data.copy()
        adjusted_data['temperature'] = round(weather_data['temperature'] + temp_adjustment, 1)
        adjusted_data['humidity'] = round(min(100, weather_data['humidity'] + humidity_adjustment), 1)
        adjusted_data['rainfall'] = round(weather_data['rainfall'] * rainfall_multiplier, 1)
        adjusted_data['elevation'] = round(elevation, 1)
        adjusted_data['microclimate_adjusted'] = True
        
        logger.info(
            f"Micro-climate adjustment: Elevation {elevation}m, "
            f"Temp {temp_adjustment:+.1f}°C, Rain {rainfall_multiplier}x"
        )
        
        return adjusted_data
    
    def _blend_with_historical(self, weather_data: Dict, lat: float) -> Dict:
        """
        Blend current API data with historical monthly patterns
        REDUCED BLENDING: 40% historical (guidance), 60% current (preserve variation)
        
        This preserves location-specific variation while still applying regional knowledge
        """
        current_month = datetime.utcnow().month
        region = self._classify_region(lat)
        
        monthly_pattern = self.MONTHLY_PATTERNS.get(current_month, {}).get(region, {})
        if not monthly_pattern:
            monthly_pattern = self.MONTHLY_PATTERNS.get(current_month, {}).get('default', {
                'temp': 23, 'humidity': 65, 'rainfall': 100
            })
        
        # Calculate annual rainfall from monthly patterns
        historical_annual_rainfall = sum(
            self.MONTHLY_PATTERNS.get(month, {}).get(region, {'rainfall': 100})['rainfall']
            for month in range(1, 13)
        )
        
        # REDUCED BLEND: 40% historical, 60% current (preserve more variation)
        blended_data = weather_data.copy()
        blended_data['temperature'] = round(
            0.4 * monthly_pattern['temp'] + 0.6 * weather_data['temperature'], 1
        )
        blended_data['humidity'] = round(
            0.4 * monthly_pattern['humidity'] + 0.6 * weather_data['humidity'], 1
        )
        blended_data['rainfall'] = round(
            0.4 * historical_annual_rainfall + 0.6 * weather_data['rainfall'], 1
        )
        blended_data['historical_blended'] = True
        blended_data['blend_ratio'] = '40% historical, 60% current'
        
        logger.debug(
            f"Historical blending (40/60): {monthly_pattern['temp']}°C (hist) + "
            f"{weather_data['temperature']}°C (curr) = {blended_data['temperature']}°C"
        )
        
        return blended_data
    
    def _calculate_soil_moisture(self, weather_data: Dict, soil_type: str) -> Dict:
        """
        Calculate soil moisture index based on rainfall, evapotranspiration, and soil retention
        
        Soil Moisture Index = (Rainfall - Evapotranspiration) * Soil Retention Factor
        
        Higher index = more available water for crops
        """
        temperature = weather_data['temperature']
        humidity = weather_data['humidity']
        rainfall = weather_data['rainfall']
        
        # Calculate potential evapotranspiration (PET) using simplified Thornthwaite method
        # PET ≈ 16 * (10*T/I)^a, where I is heat index
        # Simplified: PET (mm/year) ≈ 1.6 * (10 * T / heat_index)
        # For Kenya, rough approximation: PET = 15 * T - 200 (adjusted for tropical climate)
        evapotranspiration = max(0, 15 * temperature - 200)
        
        # Adjust for humidity (higher humidity = lower evaporation)
        humidity_factor = 1 - (humidity / 200)  # Reduce ET with high humidity
        evapotranspiration = evapotranspiration * humidity_factor
        
        # Get soil retention factor
        retention_factor = self.SOIL_RETENTION.get(soil_type, 0.30)
        
        # Calculate effective moisture (what's available after evaporation)
        effective_moisture = rainfall - evapotranspiration
        
        # Soil moisture index (accounts for soil's ability to hold water)
        soil_moisture_index = effective_moisture * retention_factor
        
        # Classify moisture level
        if soil_moisture_index > 500:
            moisture_level = 'Excellent'
        elif soil_moisture_index > 300:
            moisture_level = 'Good'
        elif soil_moisture_index > 150:
            moisture_level = 'Adequate'
        elif soil_moisture_index > 50:
            moisture_level = 'Low'
        else:
            moisture_level = 'Very Low - Irrigation Required'
        
        enhanced_data = weather_data.copy()
        enhanced_data['evapotranspiration'] = round(evapotranspiration, 1)
        enhanced_data['effective_moisture'] = round(effective_moisture, 1)
        enhanced_data['soil_retention_factor'] = retention_factor
        enhanced_data['soil_moisture_index'] = round(soil_moisture_index, 1)
        enhanced_data['moisture_level'] = moisture_level
        
        logger.info(
            f"Soil moisture: {soil_moisture_index:.0f} ({moisture_level}), "
            f"ET: {evapotranspiration:.0f}mm, Retention: {retention_factor*100:.0f}%"
        )
        
        return enhanced_data
    
    def _add_climate_indicators(self, weather_data: Dict, lat: float) -> Dict:
        """
        Add climate change indicators by comparing current vs historical averages
        """
        current_month = datetime.utcnow().month
        region = self._classify_region(lat)
        
        # Get 10-year historical average for this month/region
        historical = self.MONTHLY_PATTERNS.get(current_month, {}).get(region, {})
        if not historical:
            historical = self.MONTHLY_PATTERNS.get(current_month, {}).get('default', {
                'temp': 23, 'humidity': 65, 'rainfall': 100
            })
        
        # Calculate annual historical rainfall
        historical_annual = sum(
            self.MONTHLY_PATTERNS.get(month, {}).get(region, {'rainfall': 100})['rainfall']
            for month in range(1, 13)
        )
        
        # Temperature deviation
        temp_deviation = weather_data['temperature'] - historical['temp']
        
        # Rainfall deviation (compare to annual)
        rainfall_ratio = weather_data['rainfall'] / historical_annual if historical_annual > 0 else 1.0
        
        # Climate warnings
        warnings = []
        if temp_deviation > 2.0:
            warnings.append('Unusually warm conditions detected')
        if rainfall_ratio < 0.6:
            warnings.append('Drought risk: 40% below normal rainfall')
        elif rainfall_ratio > 1.5:
            warnings.append('Flood risk: 50% above normal rainfall')
        
        # Add to weather data
        enhanced_data = weather_data.copy()
        enhanced_data['climate_indicators'] = {
            'temperature_deviation': round(temp_deviation, 1),
            'rainfall_ratio': round(rainfall_ratio, 2),
            'warnings': warnings,
            'historical_temp': historical['temp'],
            'historical_rainfall': historical_annual
        }
        
        if warnings:
            logger.warning(f"Climate warnings: {', '.join(warnings)}")
        
        return enhanced_data
    
    def _estimate_annual_rainfall(self, lat: float) -> float:
        """Estimate annual rainfall based on latitude"""
        region = self._classify_region(lat)
        return sum(
            self.MONTHLY_PATTERNS.get(month, {}).get(region, {'rainfall': 100})['rainfall']
            for month in range(1, 13)
        )
