import { useState } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, ZAxis, Cell } from 'recharts'

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
      const response = await axios.post('/api/visualize/heatmap', {
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
      const response = await axios.post('/api/visualize/comparison', {
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
            altitude: alt / 1000, // Convert to km for display
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
    <div className="section">
      <h2>Visualization Dashboard</h2>
      <p>Explore how error changes with scale height (β) and altitude</p>
      
      <div className="input-row">
        <div className="input-group">
          <label>
            Min Altitude (m):
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
            />
          </label>
        </div>
        <div className="input-group">
          <label>
            Max Altitude (m):
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
            />
          </label>
        </div>
        <div className="input-group">
          <label>
            Optimal β (m):
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
            />
          </label>
        </div>
      </div>

      <div className="button-row">
        <button onClick={generateHeatmap} disabled={loading}>
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              Generating...
            </div>
          ) : 'Generate Error Heatmap'}
        </button>
        <button onClick={generateComparison} disabled={loading}>
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              Generating...
            </div>
          ) : 'Generate Model Comparison'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {heatmapData && (
        <div className="chart-section">
          <div className="chart-header">
            <h3>Error Landscape (β vs Altitude)</h3>
            <button 
              className="export-button"
              onClick={exportHeatmapData}
              title="Export heatmap data as CSV"
            >
              📊 Export CSV
            </button>
          </div>
          <p className="chart-description">
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
                          {data.error > 0 ? '🔴 Overestimate' : '🔵 Underestimate'}
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
        <div className="chart-section">
          <div className="chart-header">
            <h3>Model Comparison</h3>
            <button 
              className="export-button"
              onClick={exportComparisonData}
              title="Export comparison data as CSV"
            >
              📊 Export CSV
            </button>
          </div>
          
          <div className="charts-grid">
            <div>
              <h4>Pressure Profiles</h4>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={comparisonData.isa}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="altitude_km" label={{ value: 'Altitude (km)', position: 'bottom' }} />
                  <YAxis scale="log" domain={['auto', 'auto']} label={{ value: 'Pressure (Pa)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="pressure" data={comparisonData.isa} stroke="#3b82f6" name="ISA" strokeWidth={2} />
                  <Line type="monotone" dataKey="pressure" data={comparisonData.exponential_optimal} stroke="#22c55e" name={`Exp (β=${comparisonData.optimal_beta.toFixed(0)}m)`} strokeWidth={2} strokeDasharray="5 5" />
                  <Line type="monotone" dataKey="pressure" data={comparisonData.exponential_standard} stroke="#ef4444" name="Exp (β=8000m)" strokeWidth={2} strokeDasharray="3 3" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div>
              <h4>Pressure Error vs ISA</h4>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={comparisonData.isa.map((d, i) => ({
                  altitude_km: d.altitude_km,
                  optimal: comparisonData.errors_optimal[i],
                  standard: comparisonData.errors_standard[i]
                }))}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="altitude_km" label={{ value: 'Altitude (km)', position: 'bottom' }} />
                  <YAxis label={{ value: 'Error (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="optimal" stroke="#22c55e" name="Optimal β" strokeWidth={2} />
                  <Line type="monotone" dataKey="standard" stroke="#ef4444" name="Standard β=8000m" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
