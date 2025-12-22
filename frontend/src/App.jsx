import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sprout, MapPin, Target, Edit3, CheckCircle2, Loader2, 
  AlertTriangle, Calendar, TrendingUp, Droplets, ThermometerSun
} from 'lucide-react';
import { getCropRecommendation } from './services/api';

// Visual soil types with agricultural colors
const SOIL_TYPES = [
  {
    name: 'Red Volcanic',
    color: 'from-red-700 to-red-900',
    borderColor: 'border-red-700',
    description: 'Sticky, red clay',
    icon: '🔴',
    textColor: 'text-white'
  },
  {
    name: 'Black Cotton',
    color: 'from-gray-800 to-gray-950',
    borderColor: 'border-gray-800',
    description: 'Cracks when dry',
    icon: '⚫',
    textColor: 'text-white'
  },
  {
    name: 'Loam',
    color: 'from-amber-700 to-amber-900',
    borderColor: 'border-amber-700',
    description: 'Loose & fertile',
    icon: '🟤',
    textColor: 'text-white'
  },
  {
    name: 'Sandy Loam',
    color: 'from-yellow-600 to-amber-700',
    borderColor: 'border-yellow-600',
    description: 'Gritty texture',
    icon: '🟡',
    textColor: 'text-white'
  },
  {
    name: 'Clay Loam',
    color: 'from-orange-800 to-red-900',
    borderColor: 'border-orange-800',
    description: 'Sticky when wet',
    icon: '🟠',
    textColor: 'text-white'
  },
  {
    name: 'Clay',
    color: 'from-red-800 to-red-950',
    borderColor: 'border-red-800',
    description: 'Heavy, compact',
    icon: '🔴',
    textColor: 'text-white'
  },
  {
    name: 'Silty Loam',
    color: 'from-stone-600 to-stone-800',
    borderColor: 'border-stone-600',
    description: 'Smooth texture',
    icon: '🟫',
    textColor: 'text-white'
  },
  {
    name: 'Silty Clay',
    color: 'from-stone-700 to-stone-900',
    borderColor: 'border-stone-700',
    description: 'Silky feel',
    icon: '⚫',
    textColor: 'text-white'
  },
  {
    name: 'Alluvial',
    color: 'from-yellow-700 to-amber-800',
    borderColor: 'border-yellow-700',
    description: 'River deposits',
    icon: '🟨',
    textColor: 'text-white'
  },
  {
    name: 'Coastal Sandy',
    color: 'from-yellow-300 to-yellow-500',
    borderColor: 'border-yellow-400',
    description: 'Light & sandy',
    icon: '🟨',
    textColor: 'text-gray-800'
  }
];

const LOADING_MESSAGES = [
  'Scanning satellite weather data...',
  'Estimating soil nutrients...',
  'Analyzing climate patterns...',
  'Calculating best crop match...',
  'Consulting agricultural database...'
];

function App() {
  const [step, setStep] = useState('soil'); // 'soil' or 'location'
  const [location, setLocation] = useState('');
  const [soilType, setSoilType] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [locationMethod, setLocationMethod] = useState(null); // 'gps' or 'manual'
  const [detectingLocation, setDetectingLocation] = useState(false);
  const [gpsInfo, setGpsInfo] = useState(null); // Store GPS accuracy info

  // Cycle through loading messages
  useState(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setLoadingMessageIndex(prev => (prev + 1) % LOADING_MESSAGES.length);
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // Auto-detect GPS location using device GPS (not IP/browser location)
  const detectLocation = async () => {
    if (!navigator.geolocation) {
      setError('❌ GPS is not supported on your device');
      return;
    }

    // Check if we're on HTTP (not HTTPS) on mobile
    const isHTTP = window.location.protocol === 'http:';
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isHTTP && isMobile) {
      console.warn('⚠️ Running on HTTP. Some mobile browsers may block geolocation on HTTP connections.');
    }

    setDetectingLocation(true);
    setError(null);
    setGpsInfo(null);

    console.log('Starting GPS detection...');
    console.log(`Protocol: ${window.location.protocol}, User Agent: ${navigator.userAgent.substring(0, 50)}...`);

    // Use device GPS with high accuracy settings
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        
        console.log(`✅ GPS Success!`);
        console.log(`GPS Coordinates: ${latitude}, ${longitude} (Accuracy: ${accuracy}m)`);
        
        // Warn if accuracy is poor (likely WiFi/IP location, not GPS)
        if (accuracy > 100) {
          console.warn(`⚠️ Low accuracy (${accuracy}m) - likely using WiFi/IP location, not device GPS. For best results, use a mobile device or enter location manually.`);
        }
        
        // Send coordinates directly to backend - it will use Mapbox for geocoding
        const coordLocation = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
        
        console.log(`Sending coordinates to backend: ${coordLocation}`);
        
        setLocation(coordLocation);
        setLocationMethod('gps');
        setGpsInfo({ 
          accuracy: Math.round(accuracy), 
          type: accuracy > 100 ? 'wifi' : 'gps',
          coords: coordLocation
        });
        setDetectingLocation(false);
      },
      (err) => {
        console.error('GPS Error:', err);
        console.error('Error code:', err.code);
        console.error('Error message:', err.message);
        
        let errorMsg = 'GPS permission denied. Please enter location manually.';
        if (err.code === 1) {
          errorMsg = '❌ Location permission denied. Please allow location access in your browser settings and try again.';
        } else if (err.code === 2) {
          errorMsg = '❌ GPS position unavailable. Please check that location services are enabled on your device.';
        } else if (err.code === 3) {
          errorMsg = '❌ GPS timeout. Please make sure you are outdoors or near a window and try again.';
        }
        setError(errorMsg);
        setDetectingLocation(false);
      },
      { 
        enableHighAccuracy: true,  // Use GPS, not WiFi/IP location
        timeout: 15000,            // Wait up to 15 seconds
        maximumAge: 0              // Don't use cached location, get fresh GPS fix
      }
    );
  };

  // Submit prediction
  const handlePredict = async () => {
    if (!location || !soilType) {
      setError('Please complete all fields');
      return;
    }

    setLoading(true);
    setError(null);
    setLoadingMessageIndex(0);

    try {
      const data = await getCropRecommendation(location, soilType);
      
      if (data.success) {
        setResult(data);
      } else {
        setError(data.error || 'Prediction failed');
      }
    } catch (err) {
      setError(err.message || 'Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setResult(null);
    setError(null);
    setStep('soil');
    setLocation('');
    setSoilType('');
    setLocationMethod(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50">
      
      {/* LEVEL 1: HERO HEADER (Top 25% - Establishes Trust) */}
      <div className="relative h-64 bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 overflow-hidden">
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }} />
        </div>

        {/* Logo */}
        <div className="absolute top-6 left-8">
          <div className="flex items-center gap-2">
            <Sprout className="w-8 h-8 text-white" />
            <span className="text-2xl font-extrabold text-white tracking-tight">SmartGrow</span>
          </div>
        </div>

        {/* Hero Content - Centered */}
        <div className="relative h-full flex flex-col items-center justify-center text-center px-4">
          <motion.h1 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-5xl md:text-6xl font-extrabold text-white mb-3 tracking-tight"
          >
            Farming with Intelligence
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-emerald-50 font-light tracking-wide"
          >
            AI-driven crop advice for Kenyan farmers
          </motion.p>
        </div>
      </div>

      {/* LEVEL 2: ACTION CARD (Overlapping - The Workspace) */}
      <div className="relative -mt-20 px-4 pb-12">
        <main className="container mx-auto max-w-4xl">
        <AnimatePresence mode="wait">
          {!result ? (
            <motion.div
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {/* Input Form Card with Shadow-2XL */}
              <div className="bg-white rounded-3xl shadow-2xl p-8 md:p-12 border border-gray-100">
                
                {/* Error Display */}
                <AnimatePresence>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3"
                    >
                      <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <p className="text-red-800 text-sm">{error}</p>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* GPS Info Display */}
                <AnimatePresence>
                  {gpsInfo && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className={`mb-6 p-4 rounded-xl flex items-start gap-3 ${
                        gpsInfo.type === 'gps' 
                          ? 'bg-green-50 border border-green-200' 
                          : 'bg-yellow-50 border border-yellow-200'
                      }`}
                    >
                      <CheckCircle2 className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                        gpsInfo.type === 'gps' ? 'text-green-600' : 'text-yellow-600'
                      }`} />
                      <div className="flex-1">
                        <p className={`text-sm font-medium ${
                          gpsInfo.type === 'gps' ? 'text-green-800' : 'text-yellow-800'
                        }`}>
                          {gpsInfo.type === 'gps' 
                            ? `✅ GPS Location Detected (Accuracy: ${gpsInfo.accuracy}m)` 
                            : `⚠️ WiFi Location Detected (Accuracy: ${gpsInfo.accuracy}m - May be inaccurate)`
                          }
                        </p>
                        <p className={`text-xs mt-1 ${
                          gpsInfo.type === 'gps' ? 'text-green-600' : 'text-yellow-600'
                        }`}>
                          Coordinates: {gpsInfo.coords}
                        </p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* SECTION A: LOCATION (Pill Layout) */}
                <div className="mb-8">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    📍 Where is your farm?
                  </label>
                  
                  {/* Warning about GPS accuracy */}
                  <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs text-blue-800 flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                      <span>
                        <strong>Note:</strong> Auto-detect may use WiFi or network location (not always accurate). 
                        For best results, <strong>manually enter your village, town, or county name</strong>.
                      </span>
                    </p>
                  </div>
                  
                  <div className="flex flex-col md:flex-row gap-3">
                    {/* Manual Input FIRST (Primary) */}
                    <div className="flex-1">
                      <input
                        type="text"
                        value={location}
                        onChange={(e) => {
                          setLocation(e.target.value);
                          setLocationMethod('manual');
                          setGpsInfo(null); // Clear GPS info when typing manually
                        }}
                        placeholder="Enter your village, town, or county..."
                        className="w-full px-4 py-4 border-2 border-gray-300 rounded-xl focus:border-emerald-500 focus:outline-none transition-colors text-gray-700 font-medium"
                      />
                    </div>

                    {/* GPS Button SECOND (Alternative - Gray) */}
                    <div className="flex items-center gap-2">
                      <span className="text-gray-400 text-sm font-light">or</span>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={detectLocation}
                        disabled={detectingLocation}
                        className="flex items-center justify-center gap-2 px-6 py-4 bg-gray-500 hover:bg-gray-600 text-white rounded-xl font-medium shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
                      >
                        {detectingLocation ? (
                          <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>Detecting...</span>
                          </>
                        ) : (
                          <>
                            <MapPin className="w-5 h-5" />
                            <span>Auto-Detect</span>
                          </>
                        )}
                      </motion.button>
                    </div>
                  </div>
                </div>

                {/* SECTION B: SOIL (Selectable Cards - All 10 Types) */}
                <div className="mb-8">
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    🌱 What type of soil do you have?
                  </label>
                  
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                    {SOIL_TYPES.map((soil) => (
                      <motion.button
                        key={soil.name}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setSoilType(soil.name)}
                        className={`
                          relative p-6 rounded-2xl bg-gradient-to-br ${soil.color}
                          ${soil.textColor} shadow-lg transition-all duration-300
                          ${soilType === soil.name 
                            ? `ring-4 ring-emerald-500 ring-offset-2 scale-105` 
                            : 'hover:shadow-xl'
                          }
                        `}
                      >
                        {soilType === soil.name && (
                          <div className="absolute -top-2 -right-2 bg-emerald-500 rounded-full p-1">
                            <CheckCircle2 className="h-5 w-5 text-white" />
                          </div>
                        )}
                        <div className="text-4xl mb-2">{soil.icon}</div>
                        <div className="text-sm font-bold mb-1">{soil.name}</div>
                        <div className="text-xs opacity-90">{soil.description}</div>
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* PRIMARY BUTTON (Full-Width - The Finish Line) */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handlePredict}
                  disabled={!soilType || !location || loading}
                  className="w-full py-6 bg-gradient-to-r from-emerald-600 to-teal-600 text-white text-xl font-extrabold rounded-2xl shadow-2xl hover:shadow-3xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-3">
                      <Loader2 className="h-6 w-6 animate-spin" />
                      Analyzing...
                    </span>
                  ) : (
                    'GET RECOMMENDATION'
                  )}
                </motion.button>
              </div>
            </motion.div>
          ) : (
            /* Results Card */
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="space-y-6"
            >
              {/* Recommended Crop Hero Card */}
              <div className="bg-gradient-to-br from-emerald-600 to-green-700 text-white rounded-3xl shadow-2xl p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-32 translate-x-32"></div>
                <div className="relative z-10">
                  <div className="inline-block px-4 py-2 bg-white/20 rounded-full text-sm font-medium mb-4">
                    ✨ Recommended for your farm
                  </div>
                  <h2 className="text-5xl font-bold mb-4 capitalize">
                    {result.prediction}
                  </h2>
                  <div className="flex flex-wrap items-center gap-4 mb-6">
                    <div className="px-4 py-2 bg-white/20 rounded-full backdrop-blur-sm">
                      <span className="font-bold">Confidence: {(result.confidence * 100).toFixed(0)}%</span>
                    </div>
                    {result.metadata?.climate_zone && (
                      <div className="flex items-center gap-2 px-4 py-2 bg-white/20 rounded-full backdrop-blur-sm">
                        <MapPin className="h-4 w-4" />
                        <span>{result.metadata.climate_zone}</span>
                      </div>
                    )}
                    {result.metadata?.county && (
                      <div className="flex items-center gap-2 px-4 py-2 bg-white/20 rounded-full backdrop-blur-sm">
                        <span>{result.metadata.county}</span>
                      </div>
                    )}
                  </div>
                  <p className="text-lg opacity-90">
                    Optimal match for your {result.input_data?.soil_type} soil in {result.input_data?.location?.name}
                  </p>
                </div>
              </div>

              {/* Climate & Soil Analysis */}
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <ThermometerSun className="h-8 w-8 text-orange-500 mb-3" />
                  <div className="text-sm text-gray-600">Temperature</div>
                  <div className="text-2xl font-bold">
                    {result.input_data?.climate?.temperature?.toFixed(1) || result.metadata?.original_climate?.temperature?.toFixed(1)}°C
                  </div>
                </div>
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <Droplets className="h-8 w-8 text-blue-500 mb-3" />
                  <div className="text-sm text-gray-600">Rainfall</div>
                  <div className="text-2xl font-bold">
                    {result.input_data?.climate?.rainfall?.toFixed(0) || result.metadata?.original_climate?.rainfall?.toFixed(0)}mm
                  </div>
                </div>
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <TrendingUp className="h-8 w-8 text-green-500 mb-3" />
                  <div className="text-sm text-gray-600">Humidity</div>
                  <div className="text-2xl font-bold">
                    {result.input_data?.climate?.humidity?.toFixed(0) || result.metadata?.original_climate?.humidity?.toFixed(0)}%
                  </div>
                </div>
              </div>

              {/* Advisory Section */}
              {result.nutrient_analysis?.deficits && result.nutrient_analysis.deficits.length > 0 && (
                <div className="bg-amber-50 rounded-2xl shadow-lg p-6 border-2 border-amber-200">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">⚠️ Soil Advisory</h3>
                  <div className="space-y-3">
                    {result.nutrient_analysis.deficits.map((deficit, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-3 bg-white rounded-xl">
                        <AlertTriangle className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <div className="font-bold text-gray-800">{deficit}</div>
                          {result.nutrient_analysis.recommendations && result.nutrient_analysis.recommendations[idx] && (
                            <div className="text-sm text-gray-600 mt-1">{result.nutrient_analysis.recommendations[idx]}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Alternative Recommendations */}
              {result.recommendations && result.recommendations.length > 1 && (
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-4">Alternative Crops</h3>
                  <div className="grid md:grid-cols-3 gap-4">
                    {result.recommendations.slice(1, 4).map((rec, idx) => (
                      <div key={idx} className="p-4 bg-gray-50 rounded-xl border-2 border-gray-200">
                        <div className="font-bold text-lg text-gray-800">{rec.crop}</div>
                        <div className="text-emerald-600 font-medium">{(rec.confidence * 100).toFixed(0)}% match</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* New Analysis Button */}
              <button
                onClick={resetForm}
                className="w-full py-4 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700 text-white rounded-2xl font-bold text-lg shadow-lg transition-all"
              >
                🔄 New Analysis
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading Overlay */}
        <AnimatePresence>
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center"
            >
              <div className="bg-white rounded-3xl shadow-2xl p-12 max-w-md text-center">
                <Loader2 className="h-16 w-16 animate-spin text-emerald-600 mx-auto mb-6" />
                <h3 className="text-2xl font-bold text-gray-800 mb-4">Processing Your Request</h3>
                <p className="text-lg text-gray-600 animate-pulse">
                  {LOADING_MESSAGES[loadingMessageIndex]}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-amber-800 to-amber-900 text-white py-6 mt-20">
        <div className="container mx-auto px-4 text-center">
          <div className="text-lg font-medium">University of Embu</div>
          <div className="text-amber-200 text-sm">Final Year Project 2025</div>
          <div className="text-xs text-amber-300 mt-2">
            Climate-Smart Agriculture • Precision Farming • AI-Powered Recommendations
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
