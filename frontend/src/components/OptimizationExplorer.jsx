import { useState } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import HelpTooltip from './HelpTooltip'

export default function OptimizationExplorer() {
  const [minAlt, setMinAlt] = useState('0')
  const [maxAlt, setMaxAlt] = useState('20000')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const presetScenarios = [
    { name: 'Troposphere (0-12km)', min: 0, max: 12000, description: 'Commercial aviation altitudes' },
    { name: 'Low Atmosphere (0-20km)', min: 0, max: 20000, description: 'Most weather phenomena' },
    { name: 'Stratosphere (12-50km)', min: 12000, max: 50000, description: 'Ozone layer region' },
    { name: 'High Atmosphere (20-86km)', min: 20000, max: 86000, description: 'Upper atmosphere to space edge' },
    { name: 'Full ISA Range (0-86km)', min: 0, max: 86000, description: 'Complete ISA model range' }
  ]

  const validateRange = (min, max) => {
    const minNum = parseFloat(min)
    const maxNum = parseFloat(max)
    
    if (isNaN(minNum) || isNaN(maxNum)) return 'Please enter valid numbers for both altitudes'
    if (minNum < 0) return 'Minimum altitude must be non-negative'
    if (maxNum > 86000) return 'Maximum altitude must be ≤ 86,000 m (ISA limit)'
    if (minNum >= maxNum) return 'Maximum altitude must be greater than minimum altitude'
    if (maxNum - minNum < 1000) return 'Altitude range should be at least 1,000 m for meaningful optimization'
    
    return null
  }

  const optimize = async () => {
    const validationError = validateRange(minAlt, maxAlt)
    if (validationError) {
      setError(validationError)
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post('/api/optimize', {
        min_altitude: parseFloat(minAlt),
        max_altitude: parseFloat(maxAlt)
      })
      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error optimizing beta. Please check your connection and try again.')
    } finally {
      setLoading(false)
    }
  }

  const applyPreset = (preset) => {
    setMinAlt(preset.min.toString())
    setMaxAlt(preset.max.toString())
    setError(null)
    setResults(null)
  }

  const exportChartData = () => {
    if (!results) return
    
    const csvData = results.comparisons.map(comp => ({
      'Altitude (km)': comp.altitude_km,
      'ISA Pressure (Pa)': comp.isa_pressure,
      'Optimal Beta Error (%)': comp.optimal_error_pct,
      'Standard Beta Error (%)': comp.standard_error_pct
    }))
    
    const csvContent = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `optimization_results_${minAlt}-${maxAlt}m.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="card">
      <h2 className="text-3xl font-bold text-gray-800 mb-2 flex items-center">
        Optimization Explorer
        <HelpTooltip 
          content="This tool finds the optimal scale height (β) parameter for the exponential atmosphere model that best fits the ISA model over your chosen altitude range. Different altitude ranges require different β values for best accuracy."
          position="bottom"
        >
          <span className="help-icon">ℹ️</span>
        </HelpTooltip>
      </h2>
      <p className="text-gray-600 mb-6">Find the optimal scale height (β) for your altitude range</p>
      
      <div className="preset-scenarios">
        <h4 className="text-lg font-semibold text-gray-700 mb-4">📋 Common Scenarios</h4>
        <div className="preset-grid">
          {presetScenarios.map((preset, idx) => (
            <button 
              key={idx}
              className="preset-button"
              onClick={() => applyPreset(preset)}
              disabled={loading}
            >
              <div className="font-semibold text-isa-600">{preset.name}</div>
              <div className="text-sm text-gray-500">{preset.description}</div>
            </button>
          ))}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Min Altitude (m):
          </label>
          <input 
            type="number" 
            value={minAlt}
            onChange={(e) => {
              setMinAlt(e.target.value)
              if (error) setError(null)
            }}
            placeholder="e.g., 0"
            min="0"
            max="85000"
            className="input-field"
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Max Altitude (m):
          </label>
          <input 
            type="number" 
            value={maxAlt}
            onChange={(e) => {
              setMaxAlt(e.target.value)
              if (error) setError(null)
            }}
            placeholder="e.g., 20000"
            min="1000"
            max="86000"
            className="input-field"
          />
        </div>
      </div>
      
      <button 
        onClick={optimize} 
        disabled={loading}
        className="btn-primary w-full"
      >
        {loading ? (
          <div className="loading-spinner">
            <div className="spinner"></div>
            Optimizing...
          </div>
        ) : 'Optimize β'}
      </button>

      {error && <div className="error-message mt-4">{error}</div>}

      {results && (
        <div className="results">
          <div className="optimization-summary">
            <h3>Optimization Results</h3>
            <div className="summary-grid">
              <div className="summary-card optimal">
                <h4>
                  Optimal Scale Height
                  <HelpTooltip 
                    content="The scale height (β) determines how quickly pressure decreases with altitude in the exponential model. This optimized value minimizes the error between the exponential and ISA models for your chosen altitude range."
                    position="top"
                  >
                    <span className="help-icon">ℹ️</span>
                  </HelpTooltip>
                </h4>
                <p className="big-number">{results.optimization.optimal_beta.toFixed(0)} m</p>
                <p className="small-text">Best fit for {results.optimization.altitude_range_km[0]}-{results.optimization.altitude_range_km[1]} km</p>
              </div>
              <div className="summary-card">
                <h4>RMSE</h4>
                <p className="big-number">{results.optimization.rmse_percentage.toFixed(2)}%</p>
                <p className="small-text">Average error with optimal β</p>
              </div>
              <div className="summary-card">
                <h4>vs Standard β=8000m</h4>
                <p className="big-number">{(results.optimization.optimal_beta - 8000).toFixed(0)} m</p>
                <p className="small-text">{results.optimization.optimal_beta > 8000 ? 'higher' : 'lower'}</p>
              </div>
            </div>
          </div>

          <div className="comparison-table">
            <h4>Comparison at Key Altitudes</h4>
            <table>
              <thead>
                <tr>
                  <th>Altitude (km)</th>
                  <th>ISA Pressure (Pa)</th>
                  <th>Optimal β Error</th>
                  <th>Standard β Error</th>
                </tr>
              </thead>
              <tbody>
                {results.comparisons.map((comp, idx) => (
                  <tr key={idx}>
                    <td>{comp.altitude_km.toFixed(1)}</td>
                    <td>{comp.isa_pressure.toFixed(2)}</td>
                    <td className={Math.abs(comp.optimal_error_pct) < 5 ? 'success' : ''}>
                      {comp.optimal_error_pct > 0 ? '+' : ''}{comp.optimal_error_pct.toFixed(2)}%
                    </td>
                    <td className={Math.abs(comp.standard_error_pct) < 5 ? 'success' : 'warning'}>
                      {comp.standard_error_pct > 0 ? '+' : ''}{comp.standard_error_pct.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="insights">
            <h4>📚 Educational Insights</h4>
            {results.insights.map((insight, idx) => (
              <p key={idx} className="insight">• {insight}</p>
            ))}
          </div>

          <div className="chart-container">
            <div className="chart-header">
              <h4>Error Comparison</h4>
              <button 
                className="export-button"
                onClick={exportChartData}
                title="Export chart data as CSV"
              >
                📊 Export CSV
              </button>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={results.comparisons}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="altitude_km" label={{ value: 'Altitude (km)', position: 'bottom' }} />
                <YAxis label={{ value: 'Error (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="optimal_error_pct" stroke="#22c55e" name="Optimal β" strokeWidth={2} />
                <Line type="monotone" dataKey="standard_error_pct" stroke="#ef4444" name="Standard β=8000m" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
