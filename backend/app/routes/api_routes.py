
import logging
import asyncio
import json
import os
from flask import Blueprint, request, jsonify
from ..models.predictor import get_predictor

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

# Lazy load services
_api_integrator = None
_cache = None
_guidance_service = None

def get_api_integrator():
    """Lazy load API integrator"""
    global _api_integrator
    if _api_integrator is None:
        try:
            from ..services.api_integrator import APIIntegrator
            _api_integrator = APIIntegrator()
        except Exception as e:
            logger.error(f"Failed to initialize APIIntegrator: {e}")
            raise
    return _api_integrator

def get_cache():
    """Lazy load cache"""
    global _cache
    if _cache is None:
        try:
            from ..services.cache_manager import get_cache as _get_cache
            _cache = _get_cache()
        except Exception as e:
            logger.error(f"Failed to initialize cache: {e}")
            raise
    return _cache

def get_guidance_service():
    """Lazy load guidance service"""
    global _guidance_service
    if _guidance_service is None:
        try:
            from ..services.crop_guidance import CropGuidanceService
            _guidance_service = CropGuidanceService()
        except Exception as e:
            logger.error(f"Failed to initialize CropGuidanceService: {e}")
            # Return a fallback service
            class FallbackGuidanceService:
                def get_guidance(self, crop, conditions):
                    return {'success': False, 'error': f'Guidance unavailable for {crop}'}
            _guidance_service = FallbackGuidanceService()
    return _guidance_service


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


@api.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Main prediction endpoint"""
    if request.method == 'OPTIONS':
        return '', 204
        
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
            # Use get_event_loop or create new loop for asyncio operations
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            enriched_data = loop.run_until_complete(get_api_integrator().enrich_user_input(user_input))
            
            logger.info("Data enriched successfully")
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            return jsonify({'success': False, 'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Enrichment error: {e}", exc_info=True)
            return jsonify({'success': False, 'error': f'Failed to enrich data: {str(e)}'}), 500
        
        try:
            predictor = get_predictor()
            if predictor is None:
                raise ValueError("Predictor initialization failed")
            result = predictor.predict(enriched_data)
        except Exception as e:
            logger.error(f"Predictor error: {e}", exc_info=True)
            return jsonify({'success': False, 'error': f'Prediction failed: {str(e)}'}), 500
        
        if result.get('success'):
            logger.info(f"Prediction: {result['prediction']} ({result.get('confidence', 0):.2%})")
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
        cache_stats = get_cache().get_stats()
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
        get_cache().clear()
        logger.info("Cache cleared via API")
        return jsonify({'success': True, 'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    try:
        stats = get_cache().get_stats()
        return jsonify({'success': True, 'stats': stats}), 200
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/crop-guidance', methods=['POST'])
def get_crop_guidance():
    """Get detailed planting guidance for a specific crop based on conditions"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        crop = data.get('crop')
        conditions = data.get('conditions', {})

        if not crop:
            return jsonify({'success': False, 'error': 'Crop name is required'}), 400

        logger.info(f"Guidance request - Crop: {crop}, Conditions: {conditions}")

        guidance = get_guidance_service().get_guidance(crop, conditions)

        if guidance.get('success'):
            return jsonify(guidance), 200
        else:
            return jsonify(guidance), 404

    except Exception as e:
        logger.error(f"Guidance error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/crop-guidance/<crop_name>', methods=['GET'])
def get_crop_guidance_simple(crop_name):
    """Get basic crop guidance without condition adjustments"""
    try:
        guidance = get_guidance_service().get_guidance(crop_name, {})

        if guidance.get('success'):
            return jsonify(guidance), 200
        else:
            return jsonify(guidance), 404

    except Exception as e:
        logger.error(f"Guidance error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
