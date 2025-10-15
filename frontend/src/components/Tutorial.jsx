import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Tutorial() {
  const [tutorials, setTutorials] = useState(null)

  useEffect(() => {
    axios.get('/api/tutorial')
      .then(response => setTutorials(response.data))
      .catch(err => console.error(err))
  }, [])

  if (!tutorials) return <div>Loading tutorials...</div>

  return (
    <div>
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Learn About Atmospheric Modeling</h2>
      
      <div className="bg-gray-50 p-6 rounded-lg mb-8">
        <h3 className="text-2xl font-semibold text-isa-600 mb-4">{tutorials.exponential_model.title}</h3>
        {tutorials.exponential_model.sections.map((section, idx) => (
          <div key={idx} className="mb-6">
            <h4 className="text-lg font-semibold text-gray-700 mb-2">{section.heading}</h4>
            <p className="text-gray-600 leading-relaxed mb-4">{section.content}</p>
            {section.variables && (
              <div className="bg-white p-4 rounded border border-gray-200">
                {Object.entries(section.variables).map(([key, value]) => (
                  <p key={key} className="text-sm mb-2">
                    <code className="bg-gray-100 px-2 py-1 rounded text-isa-600 font-mono">{key}</code>: {value}
                  </p>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="bg-gray-50 p-6 rounded-lg mb-8">
        <h3 className="text-2xl font-semibold text-isa-600 mb-4">{tutorials.optimization.title}</h3>
        {tutorials.optimization.sections.map((section, idx) => (
          <div key={idx} className="mb-6">
            <h4 className="text-lg font-semibold text-gray-700 mb-2">{section.heading}</h4>
            <p className="text-gray-600 leading-relaxed">{section.content}</p>
          </div>
        ))}
      </div>

      <div className="insights-box">
        <h4 className="text-xl font-semibold text-blue-700 mb-4">💡 Key Takeaways</h4>
        <ul className="space-y-3 text-blue-800">
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-1">•</span>
            <span>The exponential model is simple but limited - it assumes constant temperature</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-1">•</span>
            <span>The ISA model is more accurate - it accounts for 8 atmospheric layers with different properties</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-1">•</span>
            <span>Scale height (β) can be optimized for specific altitude ranges</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-blue-500 mt-1">•</span>
            <span>No single β value fits all altitudes perfectly - this demonstrates the complexity vs accuracy tradeoff!</span>
          </li>
        </ul>
      </div>
    </div>
  )
}
