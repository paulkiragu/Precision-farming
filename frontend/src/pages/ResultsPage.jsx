import { motion } from 'framer-motion';
import { X } from 'lucide-react';

function ResultsPage({ result, onReset, onViewGuidance }) {
  return (
    <motion.div
      key="result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden"
    >
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Crop Recommendations</h1>
            <p className="text-sm text-gray-500">
              For {result.input_data?.soil_type} soil in {result.input_data?.location?.name || result.metadata?.county || 'your area'}
            </p>
          </div>
          <button
            onClick={onReset}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
          >
            <X className="h-4 w-4" />
            New Search
          </button>
        </div>
      </div>

      {/* Crops Section */}
      <div className="p-6">
        {/* Top Recommendation */}
        <div className="mb-6">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-3">Best Match</p>
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-emerald-600 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                1
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-gray-900 capitalize">{result.prediction}</h2>
                <p className="text-sm text-gray-500">
                  {(result.confidence * 100).toFixed(0)}% confidence match
                </p>
              </div>
            </div>
            <button
              onClick={() => onViewGuidance(result.prediction)}
              className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg transition-colors"
            >
              View Planting Guide
            </button>
          </div>
        </div>

        {/* Alternative Crops */}
        {result.recommendations && result.recommendations.length > 1 && (
          <div className="mb-6">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-3">Alternatives</p>
            <div className="space-y-3">
              {result.recommendations.slice(1, 5).map((rec, idx) => (
                <div
                  key={idx}
                  className="p-4 border border-gray-200 rounded-xl"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center text-gray-600 font-semibold">
                      {idx + 2}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-800 capitalize">{rec.crop}</p>
                      <p className="text-sm text-gray-400">{(rec.confidence * 100).toFixed(0)}% match</p>
                    </div>
                  </div>
                  <button
                    onClick={() => onViewGuidance(rec.crop)}
                    className="w-full py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition-colors text-sm"
                  >
                    View Planting Guide
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Divider */}
        <div className="border-t border-gray-100 my-6" />

        {/* Conditions Summary */}
        <div className="mb-6">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-3">Your Conditions</p>
          <div className="grid grid-cols-3 gap-3">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-lg font-semibold text-gray-800">
                {result.input_data?.climate?.temperature?.toFixed(0) || result.metadata?.original_climate?.temperature?.toFixed(0) || '--'}°C
              </p>
              <p className="text-xs text-gray-500">Temperature</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-lg font-semibold text-gray-800">
                {result.input_data?.climate?.rainfall?.toFixed(0) || result.metadata?.original_climate?.rainfall?.toFixed(0) || '--'}mm
              </p>
              <p className="text-xs text-gray-500">Rainfall</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-lg font-semibold text-gray-800">
                {result.input_data?.climate?.humidity?.toFixed(0) || result.metadata?.original_climate?.humidity?.toFixed(0) || '--'}%
              </p>
              <p className="text-xs text-gray-500">Humidity</p>
            </div>
          </div>
        </div>

        {/* Soil Advisory */}
        {result.nutrient_analysis?.recommendations && result.nutrient_analysis.recommendations.length > 0 && (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
            <p className="text-sm font-medium text-amber-800 mb-2">Soil Notes</p>
            <ul className="text-sm text-amber-700 space-y-1">
              {result.nutrient_analysis.recommendations.slice(0, 2).map((rec, idx) => (
                <li key={idx}>- {rec}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default ResultsPage;
