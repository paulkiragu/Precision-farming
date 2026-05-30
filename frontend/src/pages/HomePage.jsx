import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, CheckCircle2, Loader2, AlertTriangle } from 'lucide-react';
import { SOIL_TYPES } from '../constants';

function HomePage({
  location,
  setLocation,
  soilType,
  setSoilType,
  loading,
  error,
  gpsInfo,
  detectingLocation,
  onDetectLocation,
  onSubmit,
  setLocationMethod,
  setGpsInfo
}) {
  return (
    <motion.div
      key="form"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
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
              <p className="text-red-800 text-sm whitespace-pre-line">{error}</p>
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
                    ? `GPS Location Detected (Accuracy: ${gpsInfo.accuracy}m)`
                    : `WiFi/Network Location Detected (Accuracy: ${gpsInfo.accuracy}m)`
                  }
                </p>
                <p className={`text-xs mt-1 ${
                  gpsInfo.type === 'gps' ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  Coordinates: {gpsInfo.coords}
                </p>
                {gpsInfo.warning && (
                  <p className="text-xs mt-2 font-semibold text-yellow-700">
                    {gpsInfo.warning}
                  </p>
                )}
                {gpsInfo.type === 'wifi' && (
                  <p className="text-xs mt-2 font-semibold text-yellow-700">
                    Tip: If the location is wrong, please manually type your town/village name above for accurate results.
                  </p>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Location Input */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Where is your farm?
          </label>

          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1">
              <input
                type="text"
                value={location}
                onChange={(e) => {
                  setLocation(e.target.value);
                  setLocationMethod('manual');
                  setGpsInfo(null);
                }}
                placeholder="Enter your village, town, or county..."
                className="w-full px-4 py-4 border-2 border-gray-300 rounded-xl focus:border-emerald-500 focus:outline-none transition-colors text-gray-700 font-medium"
              />
            </div>

            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm font-light">or</span>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onDetectLocation}
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

        {/* Soil Selection */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            What type of soil do you have?
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
                    ? 'ring-4 ring-emerald-500 ring-offset-2 scale-105'
                    : 'hover:shadow-xl'
                  }
                `}
              >
                {soilType === soil.name && (
                  <div className="absolute -top-2 -right-2 bg-emerald-500 rounded-full p-1">
                    <CheckCircle2 className="h-5 w-5 text-white" />
                  </div>
                )}
                <div className="text-sm font-bold mb-1">{soil.name}</div>
                <div className="text-xs opacity-90">{soil.description}</div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onSubmit}
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
  );
}

export default HomePage;
