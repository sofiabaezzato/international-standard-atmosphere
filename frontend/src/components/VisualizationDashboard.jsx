import { useState } from 'react'
import api from '../services/api.js'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ZAxis, Cell } from 'recharts'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDownload, faCircle, faInfoCircle, faChartArea, faChartLine, faBullseye, faLightbulb } from '@fortawesome/free-solid-svg-icons'
import HelpPopup from './HelpPopup'

export default function VisualizationDashboard() {
  const [minAlt, setMinAlt] = useState('0')
  const [maxAlt, setMaxAlt] = useState('20000')
  const [optimalBeta, setOptimalBeta] = useState('7500')
  const [heatmapData, setHeatmapData] = useState(null)
  const [comparisonData, setComparisonData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const validateVisualizationInputs = () => {
    const minNum = parseFloat(minAlt)
    const maxNum = parseFloat(maxAlt)
    const betaNum = parseFloat(optimalBeta)
    
    if (isNaN(minNum) || isNaN(maxNum)) return 'Please enter valid altitude values'
    if (isNaN(betaNum)) return 'Please enter a valid beta value'
    if (minNum < 0) return 'Minimum altitude must be non-negative'
    if (maxNum > 86000) return 'Maximum altitude must be ≤ 86,000 m'
    if (minNum >= maxNum) return 'Maximum altitude must be greater than minimum'
    if (betaNum < 1000 || betaNum > 20000) return 'Beta should be between 1,000 and 20,000 m'
    
    return null
  }

  const generateHeatmap = async () => {
    const validationError = validateVisualizationInputs()
    if (validationError) {
      setError(validationError)
      return
    }
    
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/api/visualize/heatmap', {
        min_altitude: parseFloat(minAlt),
        max_altitude: parseFloat(maxAlt),
        num_beta: 30,
        num_alt: 30
      })
      setHeatmapData(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generating heatmap. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const generateComparison = async () => {
    const validationError = validateVisualizationInputs()
    if (validationError) {
      setError(validationError)
      return
    }
    
    setLoading(true)
    setError(null)
    try {
      const response = await api.post('/api/visualize/comparison', {
        min_altitude: parseFloat(minAlt),
        max_altitude: parseFloat(maxAlt),
        optimal_beta: parseFloat(optimalBeta)
      })
      setComparisonData(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generating comparison. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const prepareHeatmapPoints = () => {
    if (!heatmapData) return []
    
    const points = []
    heatmapData.betas.forEach((beta, bIdx) => {
      heatmapData.altitudes.forEach((alt, aIdx) => {
        const error = heatmapData.errors[aIdx][bIdx]
        if (Math.abs(error) < 50) {
          points.push({
            beta,
            altitude: alt, // Already in km from backend
            error: error,
            color: error
          })
        }
      })
    })
    return points
  }

  const getErrorColor = (error) => {
    // Color scale: Blue (negative/under) to White (zero) to Red (positive/over)
    const absError = Math.abs(error)
    const normalizedError = Math.min(absError / 20, 1) // Normalize to 0-1 for 20% max error
    
    if (error < 0) {
      // Blue scale for underestimation
      const intensity = Math.floor(255 - (normalizedError * 155))
      return `rgb(${intensity}, ${intensity}, 255)`
    } else if (error > 0) {
      // Red scale for overestimation  
      const intensity = Math.floor(255 - (normalizedError * 155))
      return `rgb(255, ${intensity}, ${intensity})`
    }
    return '#ffffff' // White for zero error
  }

  const exportHeatmapData = () => {
    if (!heatmapData) return
    
    const csvData = []
    heatmapData.betas.forEach((beta, bIdx) => {
      heatmapData.altitudes.forEach((alt, aIdx) => {
        const error = heatmapData.errors[aIdx][bIdx]
        csvData.push({
          'Beta (m)': beta,
          'Altitude (m)': alt,
          'Altitude (km)': (alt / 1000).toFixed(1),
          'Error (%)': error.toFixed(2)
        })
      })
    })
    
    const csvContent = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `heatmap_data_${minAlt}-${maxAlt}m.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  const exportComparisonData = () => {
    if (!comparisonData) return
    
    const csvData = comparisonData.isa.map((d, i) => ({
      'Altitude (km)': d.altitude_km,
      'ISA Pressure (Pa)': d.pressure,
      'ISA Temperature (K)': d.temperature,
      'ISA Density (kg/m³)': d.density,
      'Exponential Optimal Pressure (Pa)': comparisonData.exponential_optimal[i].pressure,
      'Exponential Standard Pressure (Pa)': comparisonData.exponential_standard[i].pressure,
      'Optimal Error (%)': comparisonData.errors_optimal[i],
      'Standard Error (%)': comparisonData.errors_standard[i]
    }))
    
    const csvContent = [
      Object.keys(csvData[0]).join(','),
      ...csvData.map(row => Object.values(row).join(','))
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `comparison_data_${minAlt}-${maxAlt}m.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="card">
      <h2 className="text-3xl font-bold text-gray-50 mb-2 flex items-center">
        Visualization Dashboard
        <HelpPopup 
          content={
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-white mb-2">Understanding the Visualizations</h4>
                <p className="mb-3">This dashboard helps you explore the complex relationship between atmospheric models through interactive visualizations.</p>
              </div>
              
              <div>
                <h5 className="font-semibold text-white mb-2 flex items-center">
                  <FontAwesomeIcon icon={faChartArea} className="mr-2 text-isa-400" /> Error Heatmap Analysis:
                </h5>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li><span className="font-medium">Color Coding:</span> Red areas show where the exponential model overestimates pressure, blue areas show underestimation</li>
                  <li><span className="font-medium">Sweet Spots:</span> Look for white/light areas - these represent optimal β values for specific altitudes</li>
                  <li><span className="font-medium">Patterns:</span> You'll notice diagonal bands showing how optimal β changes with altitude ranges</li>
                  <li><span className="font-medium">Insights:</span> Different atmospheric layers require different scale heights for best accuracy</li>
                </ul>
              </div>
              
              <div>
                <h5 className="font-semibold text-white mb-2 flex items-center">
                  <FontAwesomeIcon icon={faChartLine} className="mr-2 text-isa-400" /> Model Comparison Charts:
                </h5>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li><span className="font-medium">Pressure Profiles:</span> Compare ISA (blue) vs. exponential models on logarithmic scale</li>
                  <li><span className="font-medium">Error Analysis:</span> Green line shows optimized β performance, red shows standard β=8000m</li>
                  <li><span className="font-medium">Key Observations:</span> Errors typically increase with altitude and vary by atmospheric layer</li>
                  <li><span className="font-medium">Practical Use:</span> Helps determine when simple exponential models are sufficient vs. when ISA is needed</li>
                </ul>
              </div>
              
              <div>
                <h5 className="font-semibold text-white mb-2 flex items-center">
                  <FontAwesomeIcon icon={faBullseye} className="mr-2 text-isa-400" /> What to Learn:
                </h5>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>How atmospheric complexity varies with altitude</li>
                  <li>When simple models work well vs. when precision is needed</li>
                  <li>The trade-offs between model simplicity and accuracy</li>
                  <li>How to choose appropriate models for different applications</li>
                </ul>
              </div>
              
              <div className="bg-blue-900 bg-opacity-30 p-3 rounded">
                <p className="text-sm"><span className="font-medium flex items-center"><FontAwesomeIcon icon={faLightbulb} className="mr-2 text-yellow-400" /> Pro Tip:</span> Try different altitude ranges (troposphere vs. stratosphere) to see how atmospheric layers affect model accuracy. Export the data to analyze patterns in your preferred tools!</p>
              </div>
            </div>
          }
          title="Visualization Dashboard Guide"
        >
          <FontAwesomeIcon icon={faInfoCircle} className="text-isa-600 ml-2" size="2xs" />
        </HelpPopup>
      </h2>
      <p className="text-gray-400 mb-6">Explore how error changes with scale height (β) and altitude</p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div>
          <label className="block text-sm font-semibold text-gray-200 mb-2">
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
          <label className="block text-sm font-semibold text-gray-200 mb-2">
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
        <div>
          <label className="block text-sm font-semibold text-gray-200 mb-2">
            Optimal β (m):
          </label>
          <input 
            type="number" 
            value={optimalBeta}
            onChange={(e) => {
              setOptimalBeta(e.target.value)
              if (error) setError(null)
            }}
            placeholder="e.g., 7500"
            min="1000"
            max="20000"
            className="input-field"
          />
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <button 
          onClick={generateHeatmap} 
          disabled={loading}
          className="btn-primary flex-1"
        >
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              Generating...
            </div>
          ) : 'Generate Error Heatmap'}
        </button>
        <button 
          onClick={generateComparison} 
          disabled={loading}
          className="btn-primary flex-1"
        >
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              Generating...
            </div>
          ) : 'Generate Model Comparison'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {heatmapData && (
        <div className="mt-8">
          <div className="chart-header">
            <h3 className="text-2xl font-bold text-gray-50">Error Landscape (β vs Altitude)</h3>
            <button 
              className="btn-export"
              onClick={exportHeatmapData}
              title="Export heatmap data as CSV"
            >
              <FontAwesomeIcon icon={faDownload} className="mr-2" />Export CSV
            </button>
          </div>
          <p className="text-gray-400 mb-4">
            This shows how pressure error varies with different scale heights and altitudes. 
            Red = overestimate, Blue = underestimate
          </p>
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart data={prepareHeatmapPoints()}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                type="number" 
                dataKey="beta" 
                name="Scale Height β (m)" 
                domain={[5000, 12000]}
                label={{ value: 'Scale Height β (m)', position: 'insideBottom', offset: -5 }}
              />
              <YAxis 
                type="number" 
                dataKey="altitude" 
                name="Altitude (km)"
                label={{ value: 'Altitude (km)', angle: -90, position: 'insideLeft' }}
              />
              <ZAxis type="number" dataKey="error" range={[40, 80]} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} 
                content={({active, payload}) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div className="custom-tooltip">
                        <p><strong>β:</strong> {data.beta.toFixed(0)} m</p>
                        <p><strong>Altitude:</strong> {data.altitude.toFixed(1)} km</p>
                        <p><strong>Error:</strong> {data.error.toFixed(1)}%</p>
                        <p className={data.error > 0 ? 'error-over' : 'error-under'}>
                          <FontAwesomeIcon icon={faCircle} className={data.error > 0 ? 'text-red-400 mr-2' : 'text-blue-400 mr-2'} />
                          {data.error > 0 ? 'Overestimate' : 'Underestimate'}
                        </p>
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Scatter dataKey="error">
                {prepareHeatmapPoints().map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getErrorColor(entry.error)} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}

      {comparisonData && (
        <div className="mt-8">
          <div className="chart-header">
            <h3 className="text-2xl font-bold text-gray-50">Model Comparison</h3>
            <button 
              className="btn-export"
              onClick={exportComparisonData}
              title="Export comparison data as CSV"
            >
              <FontAwesomeIcon icon={faDownload} className="mr-2" />Export CSV
            </button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-6">
            <div>
              <h4 className="text-lg font-semibold text-gray-200 mb-4">Pressure Profiles</h4>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={comparisonData.isa}>
                  <CartesianGrid strokeDasharray="1 1" stroke="#374151" strokeOpacity={0.3} />
                  <XAxis 
                    dataKey="altitude_km" 
                    label={{ value: 'Altitude (km)', position: 'insideBottom', offset: -10 }}
                    type="number"
                    domain={['dataMin', 'dataMax']}
                    tickFormatter={(value) => value.toFixed(0)}
                  />
                  <YAxis 
                    scale="log" 
                    domain={['dataMin', 'dataMax']} 
                    label={{ value: 'Pressure (hPa)', angle: -90, position: 'insideLeft' }}
                    tickFormatter={(value) => (value / 100).toFixed(0)}
                  />
                  <Tooltip 
                    formatter={(value, name) => [(value / 100).toFixed(1) + ' hPa', name]}
                    labelFormatter={(value) => `Altitude: ${value.toFixed(1)} km`}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px' }} />
                  <Line 
                    type="monotone" 
                    dataKey="pressure" 
                    data={comparisonData.isa} 
                    stroke="#3b82f6" 
                    name="ISA" 
                    strokeWidth={1.5} 
                    dot={false}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="pressure" 
                    data={comparisonData.exponential_optimal} 
                    stroke="#10b981" 
                    name={`Exponential (β=${comparisonData.optimal_beta.toFixed(0)}m)`} 
                    strokeWidth={1.5} 
                    strokeDasharray="4 2" 
                    dot={false}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="pressure" 
                    data={comparisonData.exponential_standard} 
                    stroke="#ef4444" 
                    name="Exponential (β=8000m)" 
                    strokeWidth={1.5} 
                    strokeDasharray="2 2" 
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div>
              <h4 className="text-lg font-semibold text-gray-200 mb-4">Pressure Error vs ISA</h4>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={comparisonData.isa.map((d, i) => ({
                  altitude_km: d.altitude_km,
                  optimal: comparisonData.errors_optimal[i],
                  standard: comparisonData.errors_standard[i]
                }))}>
                  <CartesianGrid strokeDasharray="1 1" stroke="#374151" strokeOpacity={0.3} />
                  <XAxis 
                    dataKey="altitude_km" 
                    label={{ value: 'Altitude (km)', position: 'insideBottom', offset: -10 }}
                    type="number"
                    domain={['dataMin', 'dataMax']}
                    tickFormatter={(value) => value.toFixed(0)}
                  />
                  <YAxis 
                    label={{ value: 'Error (%)', angle: -90, position: 'insideLeft' }}
                    tickFormatter={(value) => value.toFixed(1)}
                  />
                  <Tooltip 
                    formatter={(value, name) => [value.toFixed(2) + '%', name]}
                    labelFormatter={(value) => `Altitude: ${value.toFixed(1)} km`}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px' }} />
                  <Line 
                    type="monotone" 
                    dataKey="optimal" 
                    stroke="#10b981" 
                    name="Optimized β" 
                    strokeWidth={1.5} 
                    dot={false}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="standard" 
                    stroke="#ef4444" 
                    name="Standard β=8000m" 
                    strokeWidth={1.5} 
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
