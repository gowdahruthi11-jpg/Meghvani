import React from 'react';
import { CloudRain, Sun, CloudSun, CloudDrizzle, CloudLightning, Calendar, Info } from 'lucide-react';
import { WeatherObservation } from '../types';

interface RainfallOutlookProps {
  weatherData?: WeatherObservation[];
  selectedHorizon: 7 | 14 | 21 | 30;
  onSelectHorizon: (h: 7 | 14 | 21 | 30) => void;
  isLoading?: boolean;
}

export const RainfallOutlook: React.FC<RainfallOutlookProps> = ({
  weatherData,
  selectedHorizon,
  onSelectHorizon,
  isLoading = false,
}) => {
  const horizons: Array<7 | 14 | 21 | 30> = [7, 14, 21, 30];

  // Derive daily forecast items safely from weatherData if present
  const availableDays = weatherData ? weatherData.slice(0, selectedHorizon) : [];
  const totalRainfall = availableDays.reduce((acc, curr) => acc + (curr.rainfall_mm || 0), 0);

  const getRainfallClassification = (mm: number) => {
    if (mm >= 65) return { category: 'Heavy Rain', emoji: '⛈️', color: 'text-indigo-700 bg-indigo-50 border-indigo-200' };
    if (mm >= 15) return { category: 'Moderate Rain', emoji: '🌧️', color: 'text-blue-700 bg-blue-50 border-blue-200' };
    if (mm >= 2.5) return { category: 'Light Showers', emoji: '🌦️', color: 'text-sky-700 bg-sky-50 border-sky-200' };
    if (mm > 0) return { category: 'Very Light / Trace', emoji: '⛅', color: 'text-stone-700 bg-stone-50 border-stone-200' };
    return { category: 'Dry / Clear', emoji: '☀️', color: 'text-amber-700 bg-amber-50/60 border-amber-200' };
  };

  return (
    <div className="bg-white rounded-2xl border border-stone-200/90 p-5 shadow-sm">
      {/* Title & Horizon Selector Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-stone-200 gap-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">🌧️</span>
          <div>
            <h3 className="font-bold text-stone-900 text-sm flex items-center gap-2">
              Rainfall Outlook Timeline
              <span className="text-[11px] font-normal text-stone-500 bg-stone-100 px-2 py-0.5 rounded-full">
                Weather Forecast Strip
              </span>
            </h3>
            <p className="text-xs text-stone-500">
              Multi-day precipitation sequence and dry-spell risk monitoring
            </p>
          </div>
        </div>

        {/* Horizon Selector (7D / 14D / 21D / 30D) */}
        <div className="flex items-center p-1 bg-stone-100 rounded-xl border border-stone-200 self-start sm:self-auto text-xs">
          {horizons.map((h) => (
            <button
              key={h}
              onClick={() => onSelectHorizon(h)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
                selectedHorizon === h
                  ? 'bg-forest-800 text-white shadow-xs'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              {h} Days
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="py-12 text-center text-xs text-stone-500 flex flex-col items-center justify-center space-y-2">
          <div className="w-6 h-6 border-2 border-forest-600 border-t-transparent rounded-full animate-spin" />
          <span>Loading validated rainfall observations...</span>
        </div>
      ) : availableDays.length === 0 ? (
        <div className="py-10 text-center text-xs text-stone-600 bg-stone-50 rounded-xl border border-dashed border-stone-300">
          <CloudRain className="w-8 h-8 text-stone-400 mx-auto mb-2" />
          <p className="font-semibold text-stone-800">Forecast unavailable for this block.</p>
          <p className="text-[11px] text-stone-500 mt-1">
            Rainfall pipeline requires station telemetry or active IMD historical records.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Weather Timeline Strip (Weather App Style) */}
          <div className="overflow-x-auto pb-2 scrollbar-thin">
            <div className="flex space-x-2.5 min-w-max">
              {availableDays.map((item, idx) => {
                const rain = item.rainfall_mm || 0;
                const classification = getRainfallClassification(rain);
                const dateObj = new Date(item.observation_date);
                const weekday = !isNaN(dateObj.getTime())
                  ? dateObj.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase()
                  : `DAY ${idx + 1}`;
                const dayMonth = !isNaN(dateObj.getTime())
                  ? dateObj.toLocaleDateString('en-US', { day: 'numeric', month: 'short' })
                  : '';

                return (
                  <div
                    key={item.id || idx}
                    className={`w-28 p-3 rounded-xl border flex flex-col items-center justify-between text-center transition-all hover:shadow-md ${classification.color}`}
                  >
                    {/* Day & Date */}
                    <div>
                      <span className="text-xs font-black tracking-wider block text-stone-900">
                        {weekday}
                      </span>
                      <span className="text-[10px] text-stone-500 font-medium">
                        {dayMonth}
                      </span>
                    </div>

                    {/* Weather Emoji / Icon */}
                    <div className="my-2 text-2xl transform transition-transform hover:scale-125">
                      {classification.emoji}
                    </div>

                    {/* Rainfall mm & Category */}
                    <div className="w-full">
                      <div className="text-xs font-bold text-stone-900">
                        {rain.toFixed(1)} <span className="text-[10px] font-normal text-stone-600">mm</span>
                      </div>
                      <span className="text-[10px] font-medium text-stone-600 block truncate mt-0.5">
                        {classification.category}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Quick Sub-Banner with Real Cumulative Totals */}
          <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-2.5 bg-stone-50 rounded-xl border border-stone-200 text-xs text-stone-600">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-stone-800">Horizon Summary:</span>
              <span>{availableDays.length} days evaluated</span>
              <span>·</span>
              <span className="font-bold text-rain-700">{totalRainfall.toFixed(1)} mm cumulative</span>
            </div>
            <div className="flex items-center gap-1.5 text-stone-500 text-[11px]">
              <Info className="w-3.5 h-3.5 text-forest-700" />
              <span>IMD 0.25° representative-grid telemetry</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
