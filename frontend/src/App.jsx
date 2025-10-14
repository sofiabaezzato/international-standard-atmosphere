import { useState } from 'react'
import ISACalculator from './components/ISACalculator'
import OptimizationExplorer from './components/OptimizationExplorer'
import VisualizationDashboard from './components/VisualizationDashboard'
import Tutorial from './components/Tutorial'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('calculator')

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="section-header">
        <h1 className="text-4xl font-bold mb-2">🌍 Interactive Atmosphere Model Learning Tool</h1>
        <p className="text-lg opacity-90">Explore atmospheric modeling through interactive calculations and visualizations</p>
      </header>

      <nav className="bg-gray-100 p-4 border-b-2 border-gray-200">
        <div className="max-w-7xl mx-auto flex flex-wrap gap-2">
          <button 
            className={activeTab === 'tutorial' ? 'tab-button-active' : 'tab-button'} 
            onClick={() => setActiveTab('tutorial')}
          >
            📚 Learn
          </button>
          <button 
            className={activeTab === 'calculator' ? 'tab-button-active' : 'tab-button'} 
            onClick={() => setActiveTab('calculator')}
          >
            🧮 Calculator
          </button>
          <button 
            className={activeTab === 'optimizer' ? 'tab-button-active' : 'tab-button'} 
            onClick={() => setActiveTab('optimizer')}
          >
            🔬 Optimizer
          </button>
          <button 
            className={activeTab === 'visualize' ? 'tab-button-active' : 'tab-button'} 
            onClick={() => setActiveTab('visualize')}
          >
            📊 Visualize
          </button>
        </div>
      </nav>

      <main className="flex-1 p-8 max-w-7xl mx-auto w-full">
        {activeTab === 'tutorial' && <Tutorial />}
        {activeTab === 'calculator' && <ISACalculator />}
        {activeTab === 'optimizer' && <OptimizationExplorer />}
        {activeTab === 'visualize' && <VisualizationDashboard />}
      </main>

      <footer className="bg-gray-800 text-gray-400 p-4 text-center">
        <p>Built with ISA (ISO 2533:1975) and exponential atmosphere models</p>
      </footer>
    </div>
  )
}

export default App
