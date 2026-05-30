
import axios from 'axios';

// API Base URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 *  crop recommendation from backend
 * @param {string} location 
 * @param {string} soilType 
 * @returns {Promise<Object>} 
 */
export const getCropRecommendation = async (location, soilType) => {
  try {
    const response = await axios.post(`${API_URL}/api/predict`, {
      location,
      soil_type: soilType
    });
    
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    throw new Error(
      error.response?.data?.error || 
      error.message || 
      'Failed to get crop recommendation'
    );
  }
};

/**
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/health`);
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * @returns {Promise<Array>} Soil types
 */
export const getSoilTypes = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/soil-types`);
    return response.data;
  } catch (error) {
    console.error('Failed to get soil types:', error);
    throw error;
  }
};

/**
 * list of predictable crops
 * @returns {Promise<Array>}
 */
export const getCrops = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/crops`);
    return response.data;
  } catch (error) {
    console.error('Failed to get crops:', error);
    throw error;
  }
};

/**
 * Get detailed planting guidance for a specific crop
 * @param {string} crop - Crop name
 * @param {Object} conditions - Growing conditions (rainfall, temperature, etc.)
 * @returns {Promise<Object>} Detailed guidance
 */
export const getCropGuidance = async (crop, conditions = {}) => {
  try {
    const response = await axios.post(`${API_URL}/api/crop-guidance`, {
      crop,
      conditions
    });
    return response.data;
  } catch (error) {
    console.error('Failed to get crop guidance:', error);
    throw new Error(
      error.response?.data?.error ||
      error.message ||
      'Failed to get crop guidance'
    );
  }
};

/**
 * Reverse geocode coordinates using Mapbox API
 * @param {number} latitude 
 * @param {number} longitude 
 * @returns {Promise<Object>} Location details
 */
export const reverseGeocode = async (latitude, longitude) => {
  try {
    const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;
    
    if (!MAPBOX_TOKEN) {
      throw new Error('Mapbox token not configured');
    }

    const response = await axios.get(
      `https://api.mapbox.com/geocoding/v5/mapbox.places/${longitude},${latitude}.json`,
      {
        params: {
          access_token: MAPBOX_TOKEN,
          types: 'place,locality,district,region',
          limit: 1
        }
      }
    );

    if (response.data.features && response.data.features.length > 0) {
      const feature = response.data.features[0];
      return {
        placeName: feature.place_name,
        text: feature.text,
        context: feature.context || [],
        coordinates: feature.center
      };
    }

    throw new Error('No location found');
  } catch (error) {
    console.error('Reverse geocoding error:', error);
    throw new Error(
      error.response?.data?.message || 
      error.message || 
      'Failed to get location name'
    );
  }
};

