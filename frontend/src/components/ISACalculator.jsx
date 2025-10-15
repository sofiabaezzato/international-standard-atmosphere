import { useState } from 'react'
import axios from 'axios'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faInfoCircle, faCheck, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons'
import HelpPopup from './HelpPopup'

export default function ISACalculator() {
  const [altitude, setAltitude] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const commonAltitudes = [
    { name: 'Sea Level', value: 0, description: 'Standard conditions' },
    { name: 'Denver Airport', value: 1655, description: 'High altitude airport' },
    { name: 'Mt. Everest', value: 8848, description: 'Highest mountain' },
    { name: 'Commercial Cruise', value: 11000, description: 'Typical airliner altitude' },
    { name: 'Stratosphere', value: 20000, description: 'Above weather' },
    { name: 'SR-71 Blackbird', value: 26000, description: 'High-altitude aircraft' },
    { name: 'Weather Balloon', value: 40000, description: 'Scientific measurements' }
  ]

  const validateInput = (alt) => {
    const num = parseFloat(alt)
    if (isNaN(num)) return 'Please enter a valid number'
    if (num < 0) return 'Altitude must be non-negative'
    if (num > 86000) return 'Altitude must be ≤ 86,000 m (ISA limit)'
    return null
  }

  const calculateISA = async () => {
    if (!altitude) {
      setError('Please enter an altitude value')
      return
    }
    
    const validationError = validateInput(altitude)
    if (validationError) {
      setError(validationError)
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post('/api/isa/calculate', {
        altitude: parseFloat(altitude)
      })
      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error calculating ISA parameters. Please check your connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  const selectAltitude = (alt) => {
    setAltitude(alt.value.toString())
    setError(null)
    setResults(null)
  }

  return (
    <div className="card">
      <h2 className="text-3xl font-bold text-gray-50 mb-2 flex items-center">
        ISA Calculator
        <HelpPopup 
          content="The International Standard Atmosphere (ISA) is a mathematical model defining atmospheric conditions from sea level to 86 km altitude. It uses 8 atmospheric layers with different temperature profiles to provide accurate pressure, density, and temperature calculations."
          title="International Standard Atmosphere (ISA)"
        >
          <FontAwesomeIcon icon={faInfoCircle} className="text-isa-600 ml-2" size="2xs" />
        </HelpPopup>
      </h2>
      <p className="text-gray-400 mb-6">Calculate atmospheric parameters at any altitude using the International Standard Atmosphere model</p>
      
      <div className="preset-scenarios">
        <h4 className="text-lg font-semibold text-gray-50 mb-4">Common Altitudes</h4>
        <div className="preset-grid">
          {commonAltitudes.map((alt, idx) => (
            <button 
              key={idx}
              className="preset-button"
              onClick={() => selectAltitude(alt)}
              disabled={loading}
            >
              <div className="font-semibold text-isa-600">{alt.name}</div>
              <div className="text-sm text-gray-500">{alt.value.toLocaleString()} m - {alt.description}</div>
            </button>
          ))}
        </div>
      </div>
      
      <div className="space-y-4 max-w-sm mx-auto">
        <div>
          <label className="block text-sm font-semibold text-gray-200 mb-2">
            Altitude (meters):
          </label>
          <input 
            type="number" 
            value={altitude}
            onChange={(e) => {
              setAltitude(e.target.value)
              if (error) setError(null)
            }}
            onKeyPress={(e) => {
              if (e.key === 'Enter') calculateISA()
            }}
            placeholder="e.g., 10000 (0 to 86,000 m)"
            min="0"
            max="86000"
            className="input-field"
          />
        </div>
        <button 
          onClick={calculateISA} 
          disabled={loading || !altitude}
          className="btn-primary w-full"
        >
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              Calculating...
            </div>
          ) : 'Calculate'}
        </button>
      </div>

      {error && <div className="error-message mt-4">{error}</div>}

      {loading && (
        <div className="progress-bar">
          <div className="progress-fill"></div>
        </div>
      )}

      {results && (
        <div className="mt-8">
          <h3 className="text-2xl font-bold text-gray-50 mb-6">Results at {(results.isa.geometric_altitude / 1000).toFixed(2)} km</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="result-card">
              <h4 className="text-lg font-semibold text-isa-600 mb-3 flex items-center">
                Altitude
                <HelpPopup 
                  content="Geometric altitude is the actual height above Earth's surface. Geopotential altitude accounts for Earth's curvature and gravity variations. The difference becomes significant at high altitudes."
                  title="Altitude Types"
                >
                  <FontAwesomeIcon icon={faInfoCircle} className="text-isa-600" />
                </HelpPopup>
              </h4>
              <div className="space-y-2 text-sm">
                <p><span className="font-semibold">Geometric:</span> {results.isa.geometric_altitude.toFixed(2)} m</p>
                <p><span className="font-semibold">Geopotential:</span> {results.isa.geopotential_altitude.toFixed(2)} m</p>
                <p><span className="font-semibold">Difference:</span> {results.errors.altitude_difference_m.toFixed(2)} m 
                  ({results.errors.altitude_error_pct.toFixed(3)}%)</p>
              </div>
            </div>

            <div className="result-card">
              <h4 className="text-lg font-semibold text-isa-600 mb-3">Temperature</h4>
              <div className="space-y-2 text-sm">
                <p className="text-lg font-bold">{results.isa.temperature_K.toFixed(2)} K</p>
                <p>{results.isa.temperature_C.toFixed(2)} °C</p>
                <p className="error-text">Error: {results.errors.temperature_error_pct.toFixed(3)}%</p>
              </div>
            </div>

            <div className="result-card">
              <h4 className="text-lg font-semibold text-isa-600 mb-3">Pressure</h4>
              <div className="space-y-2 text-sm">
                <p className="text-lg font-bold">{results.isa.pressure.toFixed(2)} Pa</p>
                <p>{(results.isa.pressure / 100).toFixed(2)} hPa</p>
                <p><span className="font-semibold">Ratio:</span> {results.isa.pressure_ratio.toFixed(6)}</p>
                <p className="error-text">Error: {results.errors.pressure_error_pct.toFixed(3)}%</p>
              </div>
            </div>

            <div className="result-card">
              <h4 className="text-lg font-semibold text-isa-600 mb-3">Density</h4>
              <div className="space-y-2 text-sm">
                <p className="text-lg font-bold">{results.isa.density.toFixed(4)} kg/m³</p>
                <p><span className="font-semibold">Ratio:</span> {results.isa.density_ratio.toFixed(6)}</p>
                <p className="error-text">Error: {results.errors.density_error_pct.toFixed(3)}%</p>
              </div>
            </div>

            <div className="result-card">
              <h4 className="text-lg font-semibold text-isa-600 mb-3">Speed of Sound</h4>
              <div className="space-y-2 text-sm">
                <p className="text-lg font-bold">{results.isa.speed_of_sound.toFixed(2)} m/s</p>
              </div>
            </div>

            <div className="result-card">
              <h4 className="text-lg font-semibold text-isa-600 mb-3 flex items-center">
                Exponential Model (β=8000m)
                <HelpPopup 
                  content="The exponential model simplifies the atmosphere as P(h) = P₀ × e^(-h/β), where β=8000m is the standard scale height. This is simpler than ISA but less accurate, especially at high altitudes or in regions with temperature inversions."
                  title="Exponential Atmosphere Model"
                >
                  <FontAwesomeIcon icon={faInfoCircle} className="text-isa-600" />
                </HelpPopup>
              </h4>
              <div className="space-y-2 text-sm">
                <p><span className="font-semibold">Pressure:</span> {results.exponential_comparison.pressure.toFixed(2)} Pa</p>
                <p className={`font-semibold ${Math.abs(results.exponential_comparison.error_pct) < 5 ? 'success-text' : 'error-text'}`}>
                  Error: {results.exponential_comparison.error_pct.toFixed(2)}%
                </p>
                {Math.abs(results.exponential_comparison.error_pct) < 5 ? (
                  <p className="success-text"><FontAwesomeIcon icon={faCheck} className="mr-2" />Simple model is accurate here!</p>
                ) : (
                  <p className="warning-text"><FontAwesomeIcon icon={faExclamationTriangle} className="mr-2" />Use ISA for precision</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
