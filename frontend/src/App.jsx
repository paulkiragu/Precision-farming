import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sprout, Loader2 } from 'lucide-react';
import { getCropRecommendation, reverseGeocode, getCropGuidance } from './services/api';
import { HomePage, ResultsPage, GuidancePage } from './pages';
import { LOADING_MESSAGES } from './constants';

function App() {
  const [location, setLocation] = useState('');
  const [soilType, setSoilType] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [locationMethod, setLocationMethod] = useState(null);
  const [detectingLocation, setDetectingLocation] = useState(false);
  const [gpsInfo, setGpsInfo] = useState(null);

  // Guidance state
  const [guidanceModal, setGuidanceModal] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [guidanceData, setGuidanceData] = useState(null);
  const [loadingGuidance, setLoadingGuidance] = useState(false);

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

  // Auto-detect GPS location
  const detectLocation = async () => {
    if (!navigator.geolocation) {
      setError('GPS is not supported on your device');
      return;
    }

    setDetectingLocation(true);
    setError(null);
    setGpsInfo(null);

    const isMobileUserAgent = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const hasTouchScreen = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    const isMobile = isMobileUserAgent && hasTouchScreen;

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        const coordLocation = `${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;

        try {
          const locationData = await reverseGeocode(latitude, longitude);
          const hasAccuracy = typeof accuracy === 'number' && !isNaN(accuracy);
          const place = (locationData && (locationData.placeName || locationData.text)) || coordLocation;

          setLocation(place);
          setLocationMethod('gps');
          setGpsInfo({
            accuracy: hasAccuracy ? Math.round(accuracy) : null,
            type: isMobile ? 'gps' : 'wifi',
            coords: coordLocation,
            placeName: locationData?.placeName,
            warning: !isMobile ? 'Desktop WiFi location may be inaccurate - please verify and correct if needed' : null
          });
          setError(null);
          setDetectingLocation(false);
        } catch (err) {
          setLocation(coordLocation);
          setLocationMethod('gps');
          setGpsInfo({ accuracy: typeof accuracy === 'number' ? Math.round(accuracy) : null, type: 'unknown', coords: coordLocation });
          setError('Could not resolve a place name. Using coordinates.');
          setDetectingLocation(false);
        }
      },
      (err) => {
        let errorMsg = 'Could not get your location.';
        if (err.code === 1) {
          errorMsg = 'Location permission denied. Please enable location access and try again.';
        } else if (err.code === 2) {
          errorMsg = 'Location unavailable. Please check your GPS/WiFi settings.';
        } else if (err.code === 3) {
          errorMsg = 'Location request timed out. Please try again.';
        }
        setError(errorMsg);
        setGpsInfo(null);
        setDetectingLocation(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0
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
    setLocation('');
    setSoilType('');
    setLocationMethod(null);
    setGuidanceModal(false);
    setSelectedCrop(null);
    setGuidanceData(null);
  };

  // Fetch crop guidance
  const fetchCropGuidance = async (cropName) => {
    setSelectedCrop(cropName);
    setGuidanceModal(true);
    setLoadingGuidance(true);
    setGuidanceData(null);

    try {
      const conditions = {
        rainfall: result?.input_data?.climate?.rainfall || result?.metadata?.original_climate?.rainfall,
        temperature: result?.input_data?.climate?.temperature || result?.metadata?.original_climate?.temperature,
        humidity: result?.input_data?.climate?.humidity || result?.metadata?.original_climate?.humidity,
        soil_type: result?.input_data?.soil_type,
        climate_zone: result?.metadata?.climate_zone
      };

      const data = await getCropGuidance(cropName, conditions);

      if (data.success) {
        setGuidanceData(data);
      } else {
        setGuidanceData({ error: data.error || 'Failed to load guidance' });
      }
    } catch (err) {
      setGuidanceData({ error: err.message || 'Failed to load guidance' });
    } finally {
      setLoadingGuidance(false);
    }
  };

  // Close guidance
  const closeGuidanceModal = () => {
    setGuidanceModal(false);
    setSelectedCrop(null);
    setGuidanceData(null);
  };

  // Render guidance page
  if (guidanceModal) {
    return (
      <GuidancePage
        selectedCrop={selectedCrop}
        guidanceData={guidanceData}
        loadingGuidance={loadingGuidance}
        onClose={closeGuidanceModal}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50">
      {/* Header */}
      <div className="relative h-64 bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '40px 40px'
          }} />
        </div>

        <div className="absolute top-6 left-8">
          <div className="flex items-center gap-2">
            <Sprout className="w-8 h-8 text-white" />
            <span className="text-2xl font-extrabold text-white tracking-tight">SmartGrow</span>
          </div>
        </div>

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

      {/* Main Content */}
      <div className="relative px-4 pb-12 -mt-20">
        <main className="container mx-auto max-w-4xl">
          <AnimatePresence mode="wait">
            {!result ? (
              <HomePage
                location={location}
                setLocation={setLocation}
                soilType={soilType}
                setSoilType={setSoilType}
                loading={loading}
                error={error}
                gpsInfo={gpsInfo}
                detectingLocation={detectingLocation}
                onDetectLocation={detectLocation}
                onSubmit={handlePredict}
                setLocationMethod={setLocationMethod}
                setGpsInfo={setGpsInfo}
              />
            ) : (
              <ResultsPage
                result={result}
                onReset={resetForm}
                onViewGuidance={fetchCropGuidance}
              />
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
          <div className="text-lg font-medium">Precision Farming</div>
          <div className="text-amber-200 text-sm"><span>&#xA9;</span> 2026</div>
          <div className="text-xs text-amber-300 mt-2">
            Precision Farming - AI-Powered Recommendations
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
