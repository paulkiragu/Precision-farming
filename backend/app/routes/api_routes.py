"""
API Routes
Flask Blueprint for crop recommendation endpoints
"""

import logging
import asyncio
from flask import Blueprint, request, jsonify
from ..services.api_integrator import APIIntegrator
from ..models.predictor import get_predictor
from ..services.cache_manager import get_cache

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)
api_integrator = APIIntegrator()
cache = get_cache()


def parse_location(location_input):
    """Parse location input - can be name or coordinates"""
    if isinstance(location_input, dict):
        return {'type': 'coords', 'value': location_input}
    
    if isinstance(location_input, str):
        if ',' in location_input:
            try:
                parts = location_input.split(',')
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                return {'type': 'coords', 'value': {'lat': lat, 'lon': lon}}
            except (ValueError, IndexError):
                return {'type': 'name', 'value': location_input}
        else:
            return {'type': 'name', 'value': location_input}
    
    raise ValueError("Invalid location format")


@api.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        location_input = data.get('location')
        soil_type = data.get('soil_type')
        
        if not location_input:
            return jsonify({'success': False, 'error': 'Location is required'}), 400
        
        if not soil_type:
            return jsonify({'success': False, 'error': 'Soil type is required'}), 400
        
        logger.info(f"Prediction request - Location: {location_input}, Soil: {soil_type}")
        
        try:
            parsed_location = parse_location(location_input)
            logger.info(f"Parsed location type: {parsed_location['type']}")
        except ValueError as e:
            return jsonify({'success': False, 'error': f'Invalid location format: {str(e)}'}), 400
        
        user_input = {
            'location': parsed_location['value'],
            'soil_type': soil_type
        }
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            enriched_data = loop.run_until_complete(api_integrator.enrich_user_input(user_input))
            loop.close()
            
            logger.info("Data enriched successfully")
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 400
        
        predictor = get_predictor()
        result = predictor.predict(enriched_data)
        
        if result.get('success'):
            logger.info(f"Prediction: {result['prediction']} ({result['confidence']:.2%})")
            return jsonify(result), 200
        else:
            logger.error(f"Prediction failed: {result.get('error')}")
            return jsonify(result), 500
        
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        cache_stats = cache.get_stats()
        return jsonify({
            'status': 'healthy',
            'service': 'Kenyan Crop Recommendation API',
            'version': '1.0.0',
            'cache_stats': cache_stats
        }), 200
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@api.route('/soil-types', methods=['GET'])
def get_soil_types():
    """Get list of supported soil types"""
    try:
        from ..services.soil_heuristic import SoilHeuristicService
        
        soil_service = SoilHeuristicService()
        soil_types = []
        
        for soil_name in soil_service.get_available_soil_types():
            nutrients = soil_service.get_nutrients_from_soil(soil_name)
            if nutrients:
                soil_types.append({
                    'name': soil_name,
                    'description': nutrients.get('description', ''),
                    'nutrients': {
                        'N': nutrients.get('N'),
                        'P': nutrients.get('P'),
                        'K': nutrients.get('K'),
                        'pH': nutrients.get('pH')
                    }
                })
        
        return jsonify({'success': True, 'soil_types': soil_types, 'count': len(soil_types)}), 200
    except Exception as e:
        logger.error(f"Soil types error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/crops', methods=['GET'])
def get_crops():
    """Get list of predictable crops"""
    try:
        predictor = get_predictor()
        crops = predictor.get_supported_crops()
        return jsonify({'success': True, 'crops': sorted(crops), 'count': len(crops)}), 200
    except Exception as e:
        logger.error(f"Crops list error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear API cache"""
    try:
        cache.clear()
        logger.info("Cache cleared via API")
        return jsonify({'success': True, 'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    try:
        stats = cache.get_stats()
        return jsonify({'success': True, 'stats': stats}), 200
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
