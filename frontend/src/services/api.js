/**
 * API Service - Backend Integration
 * Handles all HTTP requests to the Flask backend
 */

import axios from 'axios';

// API Base URL - defaults to localhost:5000
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Get crop recommendation from backend
 * @param {string} location - Location name or coordinates
 * @param {string} soilType - Type of soil
 * @returns {Promise<Object>} Prediction result
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
 * Check backend health status
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
 * Get list of supported soil types
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
 * Get list of predictable crops
 * @returns {Promise<Array>} Crops
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

export default {
  getCropRecommendation,
  checkHealth,
  getSoilTypes,
  getCrops
};
