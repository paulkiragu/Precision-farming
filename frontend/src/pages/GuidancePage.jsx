import { Loader2, AlertTriangle, ArrowLeft, Info, Shovel, CheckCircle2, Leaf, Ban, Lightbulb } from 'lucide-react';

function GuidancePage({ selectedCrop, guidanceData, loadingGuidance, onClose }) {
  return (
    <div className="min-h-screen bg-white">
      {/* Page Header */}
      <div className="bg-gradient-to-r from-emerald-600 to-green-700 text-white px-6 py-5">
        <div className="flex items-center gap-4">
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-xl font-bold capitalize">{selectedCrop} Planting Guide</h1>
            <p className="text-emerald-100 text-sm">Adjusted for your local conditions</p>
          </div>
        </div>
      </div>

      {/* Page Content */}
      <div className="p-6">
        {loadingGuidance ? (
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-12 w-12 animate-spin text-emerald-600 mb-4" />
            <p className="text-gray-600">Loading planting guidance...</p>
          </div>
        ) : guidanceData?.error ? (
          <div className="text-center py-16">
            <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-4" />
            <p className="text-gray-800 font-medium">{guidanceData.error}</p>
            <p className="text-gray-500 text-sm mt-2">Detailed guidance for this crop is not yet available.</p>
            <button
              onClick={onClose}
              className="mt-6 px-6 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg transition-colors"
            >
              Back to Results
            </button>
          </div>
        ) : guidanceData ? (
          <div className="space-y-6">
            {/* Condition Notes */}
            {guidanceData.condition_notes && guidanceData.condition_notes.length > 0 && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <h3 className="font-bold text-blue-800 mb-2 flex items-center gap-2">
                  <Info className="h-5 w-5" />
                  Based on Your Conditions
                </h3>
                <ul className="space-y-1">
                  {guidanceData.condition_notes.map((note, idx) => (
                    <li key={idx} className="text-blue-700 text-sm">{note}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Planting Instructions */}
            {guidanceData.planting && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                <h3 className="font-bold text-emerald-800 mb-3 flex items-center gap-2">
                  <Shovel className="h-5 w-5" />
                  Planting Instructions
                </h3>

                {/* Parameters Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
                  {guidanceData.planting.parameters?.hole_width_cm && (
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-emerald-700">{guidanceData.planting.parameters.hole_width_cm}cm</div>
                      <div className="text-xs text-gray-600">Hole Width</div>
                    </div>
                  )}
                  {guidanceData.planting.parameters?.hole_depth_cm && (
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-emerald-700">{guidanceData.planting.parameters.hole_depth_cm}cm</div>
                      <div className="text-xs text-gray-600">Hole Depth</div>
                    </div>
                  )}
                  {guidanceData.planting.parameters?.spacing_row_cm && (
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-emerald-700">{guidanceData.planting.parameters.spacing_row_cm}cm</div>
                      <div className="text-xs text-gray-600">Row Spacing</div>
                    </div>
                  )}
                  {guidanceData.planting.parameters?.spacing_plant_cm && (
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-emerald-700">{guidanceData.planting.parameters.spacing_plant_cm}cm</div>
                      <div className="text-xs text-gray-600">Plant Spacing</div>
                    </div>
                  )}
                  {guidanceData.planting.parameters?.seeds_per_hole && (
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-emerald-700">{guidanceData.planting.parameters.seeds_per_hole}</div>
                      <div className="text-xs text-gray-600">Seeds/Hole</div>
                    </div>
                  )}
                  {guidanceData.planting.parameters?.spacing_row_m && (
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-emerald-700">{guidanceData.planting.parameters.spacing_row_m}m</div>
                      <div className="text-xs text-gray-600">Row Spacing</div>
                    </div>
                  )}
                  {guidanceData.planting.parameters?.spacing_plant_m && (
                    <div className="bg-white rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-emerald-700">{guidanceData.planting.parameters.spacing_plant_m}m</div>
                      <div className="text-xs text-gray-600">Plant Spacing</div>
                    </div>
                  )}
                </div>

                {/* Adjustment Reasons */}
                {guidanceData.planting.adjustment_reasons && guidanceData.planting.adjustment_reasons.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-emerald-200">
                    <p className="text-sm font-medium text-emerald-800 mb-2">Adjustments for your conditions:</p>
                    <ul className="space-y-1">
                      {guidanceData.planting.adjustment_reasons.map((reason, idx) => (
                        <li key={idx} className="text-sm text-emerald-700 flex items-start gap-2">
                          <CheckCircle2 className="h-4 w-4 mt-0.5 flex-shrink-0" />
                          {reason}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Fertilizers */}
            {guidanceData.fertilizers && Object.keys(guidanceData.fertilizers).length > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <h3 className="font-bold text-amber-800 mb-3 flex items-center gap-2">
                  <Leaf className="h-5 w-5" />
                  Fertilizer Recommendations
                </h3>
                <div className="space-y-3">
                  {Object.entries(guidanceData.fertilizers).map(([key, fert]) => (
                    <div key={key} className="bg-white rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-bold text-amber-800 capitalize">{key.replace(/_/g, ' ')}</span>
                        <span className="text-xs bg-amber-200 text-amber-800 px-2 py-1 rounded-full">{fert.timing}</span>
                      </div>
                      <div className="text-sm text-gray-700">
                        <p><strong>Type:</strong> {fert.type}</p>
                        {fert.rate_kg_per_acre && <p><strong>Rate:</strong> {fert.rate_kg_per_acre} kg/acre</p>}
                        {fert.rate_g_per_plant && <p><strong>Rate:</strong> {fert.rate_g_per_plant}g per plant</p>}
                        {fert.rate_kg_per_hole && <p><strong>Rate:</strong> {fert.rate_kg_per_hole}kg per hole</p>}
                        {fert.rate_kg_per_tree && <p><strong>Rate:</strong> {fert.rate_kg_per_tree}kg per tree</p>}
                        <p><strong>Application:</strong> {fert.application}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* What to Avoid */}
            {guidanceData.avoid && guidanceData.avoid.length > 0 && (
              <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
                <h3 className="font-bold text-orange-800 mb-3 flex items-center gap-2">
                  <Ban className="h-5 w-5" />
                  What to Avoid
                </h3>
                <ul className="space-y-2">
                  {guidanceData.avoid.map((item, idx) => (
                    <li key={idx} className="text-sm text-orange-700 pl-4 border-l-2 border-orange-300">
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Best Practices */}
            {guidanceData.best_practices && guidanceData.best_practices.length > 0 && (
              <div className="bg-teal-50 border border-teal-200 rounded-xl p-4">
                <h3 className="font-bold text-teal-800 mb-3 flex items-center gap-2">
                  <Lightbulb className="h-5 w-5" />
                  Best Practices
                </h3>
                <ul className="space-y-2">
                  {guidanceData.best_practices.map((practice, idx) => (
                    <li key={idx} className="text-sm text-teal-700 pl-4 border-l-2 border-teal-300">
                      {practice}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Back Button */}
            <div className="pt-4 pb-8">
              <button
                onClick={onClose}
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Recommendations
              </button>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default GuidancePage;
