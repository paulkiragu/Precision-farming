"""
Cache Manager - Enhanced with Time-Aware TTL and Regional Sharing
Simple in-memory caching with intelligent expiration for different data types
Includes predictive cache warming and regional cache sharing
"""

import time
from typing import Any, Optional, Dict, List
import logging
import json
import hashlib
import math

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Enhanced in-memory cache with intelligent TTL management
    
    Features:
    - Time-aware expiration: Different TTLs for different data types
    - Regional sharing: Nearby locations (<5km) share weather data
    - Predictive warming: Pre-fetch common Kenya locations
    - Auto-cleanup of expired entries
    """
    
    # Smart TTL values (in seconds)
    TTL_WEATHER = 3 * 3600      # 3 hours (weather changes)
    TTL_GEOCODING = 30 * 86400  # 30 days (coordinates don't change)
    TTL_SOIL = 24 * 3600        # 24 hours (static data, refresh daily)
    TTL_ELEVATION = 90 * 86400  # 90 days (terrain doesn't change)
    
    # Regional sharing distance (km)
    REGIONAL_DISTANCE_KM = 5.0  # Share weather within 5km radius
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize enhanced cache manager
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0
        self._regional_hits = 0  # New: track regional cache sharing
        
        # Pre-warm cache with common Kenya locations
        self._warmup_locations = [
            'nairobi', 'mombasa', 'kisumu', 'nakuru', 'eldoret',
            'thika', 'malindi', 'kakamega', 'kericho', 'nyeri'
        ]
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Create a unique key from arguments
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key in self._cache:
            entry = self._cache[key]
            
            # Check if expired
            if time.time() < entry['expires_at']:
                self._hits += 1
                logger.debug(f"Cache HIT: {key}")
                return entry['value']
            else:
                # Expired, remove it
                del self._cache[key]
                logger.debug(f"Cache EXPIRED: {key}")
        
        self._misses += 1
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default_ttl if None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache DELETE: {key}")
    
    def clear(self):
        """Clear entire cache"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache cleared")
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time >= entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced cache statistics"""
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        regional_rate = (self._regional_hits / total_requests * 100) if total_requests > 0 else 0
        
        # Count entries by type
        weather_count = sum(1 for k in self._cache.keys() if k.startswith('weather:'))
        geocoding_count = sum(1 for k in self._cache.keys() if k.startswith('geocoding:'))
        elevation_count = sum(1 for k in self._cache.keys() if k.startswith('elevation:'))
        
        return {
            'weather': {
                'size': weather_count,
                'hits': self._hits,
                'misses': self._misses,
                'regional_hits': self._regional_hits
            },
            'geocoding': {
                'size': geocoding_count
            },
            'elevation': {
                'size': elevation_count
            },
            'overall': {
                'size': len(self._cache),
                'hits': self._hits,
                'misses': self._misses,
                'regional_hits': self._regional_hits,
                'hit_rate': round(hit_rate, 2),
                'regional_hit_rate': round(regional_rate, 2),
                'total_requests': total_requests
            }
        }
    
    # Enhanced context-specific cache methods
    
    def cache_weather(self, lat: float, lon: float, data: Dict, ttl: Optional[int] = None):
        """
        Cache weather data with smart TTL
        
        Args:
            lat: Latitude
            lon: Longitude
            data: Weather data dict
            ttl: Custom TTL (uses TTL_WEATHER if None)
        """
        if ttl is None:
            ttl = self.TTL_WEATHER
        
        key = self._generate_key('weather', lat=round(lat, 4), lon=round(lon, 4))
        
        # Store with coordinates for regional sharing
        cache_entry = data.copy()
        cache_entry['_cache_lat'] = lat
        cache_entry['_cache_lon'] = lon
        
        self.set(key, cache_entry, ttl)
        logger.debug(f"Weather cached for ({lat:.4f}, {lon:.4f}), TTL: {ttl}s")
    
    def get_cached_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get cached weather with regional sharing
        
        Checks:
        1. Exact location match
        2. Nearby locations within REGIONAL_DISTANCE_KM
        """
        # Try exact match first
        key = self._generate_key('weather', lat=round(lat, 4), lon=round(lon, 4))
        exact_match = self.get(key)
        
        if exact_match:
            return exact_match
        
        # Try regional sharing - find nearby cached locations
        nearby_weather = self._find_nearby_weather(lat, lon)
        if nearby_weather:
            self._regional_hits += 1
            logger.info(f"Regional cache HIT: Using weather from nearby location")
            return nearby_weather
        
        return None
    
    def _find_nearby_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Find weather data from nearby locations within REGIONAL_DISTANCE_KM"""
        current_time = time.time()
        
        for key, entry in self._cache.items():
            if not key.startswith('weather:'):
                continue
            
            # Check if expired
            if current_time >= entry['expires_at']:
                continue
            
            data = entry['value']
            if '_cache_lat' not in data or '_cache_lon' not in data:
                continue
            
            # Calculate distance
            distance = self._haversine_distance(
                lat, lon,
                data['_cache_lat'], data['_cache_lon']
            )
            
            if distance <= self.REGIONAL_DISTANCE_KM:
                logger.debug(f"Found nearby weather {distance:.1f}km away")
                return data
        
        return None
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance between two points (in km)
        Using Haversine formula
        """
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c
        
        return distance
    
    def cache_geocoding(self, location: str, data: Dict, ttl: Optional[int] = None):
        """
        Cache geocoding result with smart TTL
        
        Args:
            location: Location name
            data: Geocoding data
            ttl: Custom TTL (uses TTL_GEOCODING if None - 30 days)
        """
        if ttl is None:
            ttl = self.TTL_GEOCODING
        
        key = self._generate_key('geocoding', location=location.lower())
        self.set(key, data, ttl)
        logger.debug(f"Geocoding cached for '{location}', TTL: {ttl}s")
    
    def get_cached_geocoding(self, location: str) -> Optional[Dict]:
        """Get cached geocoding result"""
        key = self._generate_key('geocoding', location=location.lower())
        return self.get(key)


# Global cache instance
_cache_instance = None

def get_cache() -> CacheManager:
    """Get global cache instance (singleton pattern)"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager(default_ttl=3600)  # 1 hour default
    return _cache_instance
