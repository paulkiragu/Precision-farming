"""
Geocoding Service - Hybrid Mapbox + Nominatim
Converts location names to coordinates (Lat/Lon)
Uses Mapbox first (accurate, $0.50/1000), falls back to Nominatim (free) if Mapbox unavailable
"""

import aiohttp
import logging
import os
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class GeocodingService:
    """Service for converting location names to coordinates"""
    
    # Nominatim (OpenStreetMap) - Free but less accurate for Kenya
    NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
    NOMINATIM_REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
    USER_AGENT = "KenyanCropRecommendation/1.0 (Educational Project)"
    
    # Mapbox - $0.50 per 1000 requests, better accuracy
    MAPBOX_GEOCODING_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY')  # Set in .env file
    
    # Kenya boundaries for validation
    KENYA_LAT_MIN = -4.6795
    KENYA_LAT_MAX = 5.0332
    KENYA_LON_MIN = 33.9098
    KENYA_LON_MAX = 41.8992
    
    # Distance threshold for "poor" results (km)
    ACCURACY_THRESHOLD = 20.0
    
    async def get_coordinates(self, location_name: str) -> Optional[Dict[str, float]]:
        """
        Convert location name to coordinates
        Uses Mapbox first (accurate, $0.50/1000), falls back to Nominatim (free) if Mapbox fails
        
        Args:
            location_name: Name of location (e.g., "Nakuru", "Kevote Trading Center")
            
        Returns:
            Dict with 'lat' and 'lon' keys, or None if not found
        """
        # Try Mapbox first if configured (more accurate for Kenya)
        if self.MAPBOX_API_KEY:
            logger.info(f"Trying Mapbox for '{location_name}'")
            mapbox_coords = await self._geocode_mapbox(location_name)
            if mapbox_coords:
                logger.info(f"✓ Mapbox succeeded for '{location_name}'")
                return mapbox_coords
            else:
                logger.info(f"Mapbox failed for '{location_name}', trying Nominatim fallback")
        
        # Fallback to Nominatim (free but less accurate)
        coords = await self._geocode_nominatim(location_name)
        
        # Return Nominatim result (could be None)
        if coords:
            coords.pop('confidence', None)  # Remove internal metadata
            logger.info(f"✓ Nominatim fallback succeeded for '{location_name}'")
        else:
            logger.warning(f"✗ Both Mapbox and Nominatim failed for '{location_name}'")
        
        return coords
    
    async def _geocode_nominatim(self, location_name: str) -> Optional[Dict[str, float]]:
        """Geocode using Nominatim (OpenStreetMap) - Free"""
        try:
            params = {
                'q': f"{location_name}, Kenya",
                'format': 'json',
                'limit': 1,
                'countrycodes': 'ke'  # Restrict to Kenya
            }
            
            headers = {
                'User-Agent': self.USER_AGENT
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.NOMINATIM_SEARCH_URL,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if data and len(data) > 0:
                        result = data[0]
                        lat = float(result['lat'])
                        lon = float(result['lon'])
                        
                        # Validate within Kenya boundaries
                        if self._is_within_kenya(lat, lon):
                            logger.info(f"Nominatim: '{location_name}' → ({lat}, {lon})")
                            
                            # Mark confidence based on result type
                            confidence = 'high' if result.get('importance', 0) > 0.5 else 'low'
                            
                            return {'lat': lat, 'lon': lon, 'confidence': confidence}
                        else:
                            logger.warning(f"Location '{location_name}' outside Kenya boundaries")
                            return None
                    else:
                        logger.warning(f"Nominatim: No results for '{location_name}'")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"Nominatim API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Nominatim unexpected error: {e}")
            return None
    
    async def _geocode_mapbox(self, location_name: str) -> Optional[Dict[str, float]]:
        """Geocode using Mapbox - $0.50 per 1000 requests"""
        if not self.MAPBOX_API_KEY:
            return None
        
        try:
            # Mapbox format: /mapbox.places/{query}.json
            query = f"{location_name} Kenya"
            url = f"{self.MAPBOX_GEOCODING_URL}/{query}.json"
            
            params = {
                'access_token': self.MAPBOX_API_KEY,
                'country': 'KE',  # Restrict to Kenya
                'limit': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if data.get('features') and len(data['features']) > 0:
                        feature = data['features'][0]
                        coordinates = feature['geometry']['coordinates']
                        lon, lat = coordinates  # Mapbox returns [lon, lat]
                        
                        # Validate within Kenya boundaries
                        if self._is_within_kenya(lat, lon):
                            logger.info(f"Mapbox: '{location_name}' → ({lat}, {lon})")
                            return {'lat': lat, 'lon': lon}
                        else:
                            logger.warning(f"Mapbox: Location '{location_name}' outside Kenya")
                            return None
                    else:
                        logger.warning(f"Mapbox: No results for '{location_name}'")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"Mapbox API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Mapbox unexpected error: {e}")
            return None
    
    def _is_within_kenya(self, lat: float, lon: float) -> bool:
        """Validate coordinates are within Kenya"""
        return (
            self.KENYA_LAT_MIN <= lat <= self.KENYA_LAT_MAX and
            self.KENYA_LON_MIN <= lon <= self.KENYA_LON_MAX
        )
    
    async def get_county_from_coordinates(self, lat: float, lon: float) -> Optional[str]:
        """
        Reverse geocode coordinates to get county name
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            County name (e.g., "Embu County") or None if not found
        """
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'zoom': 10,  # County level
                'addressdetails': 1
            }
            
            headers = {
                'User-Agent': self.USER_AGENT
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.NOMINATIM_REVERSE_URL,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if data and 'address' in data:
                        address = data['address']
                        
                        # Try to get county from various address fields
                        # Nominatim may return county in different fields
                        county = (
                            address.get('county') or
                            address.get('state_district') or
                            address.get('state')
                        )
                        
                        if county:
                            # Ensure it ends with "County" if it doesn't already
                            if not county.lower().endswith('county'):
                                county = f"{county} County"
                            
                            logger.info(f"Reverse geocoded ({lat}, {lon}) to {county}")
                            return county
                        else:
                            logger.warning(f"No county found in address data for ({lat}, {lon})")
                            return None
                    else:
                        logger.warning(f"No address data found for ({lat}, {lon})")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"Reverse geocoding API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected reverse geocoding error: {e}")
            return None
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Public method to validate coordinates"""
        return self._is_within_kenya(lat, lon)
