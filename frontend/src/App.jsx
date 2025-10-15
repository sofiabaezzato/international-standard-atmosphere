import { useState } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faHeart } from '@fortawesome/free-solid-svg-icons'
import ISACalculator from './components/ISACalculator'
import OptimizationExplorer from './components/OptimizationExplorer'
import VisualizationDashboard from './components/VisualizationDashboard'
import Tutorial from './components/Tutorial'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('calculator')

  return (
    <div className="h-screen w-screen flex flex-col bg-atmosphere-900 overflow-hidden">
      <header className="section-header flex-shrink-0">
        <h1 className="text-3xl font-bold mb-2">Interactive Atmosphere Model Learning Tool</h1>
        <p className="text-md opacity-90">Explore atmospheric modeling through interactive calculations and visualizations</p>
          <nav className="mt-2 flex min-w-full">
            <div className="w-full flex flex-wrap gap-2 items-center justify-items-center">
              {/*<button*/}
              {/*  className={activeTab === 'tutorial' ? 'tab-button-active' : 'tab-button'}*/}
              {/*  onClick={() => setActiveTab('tutorial')}*/}
              {/*>*/}
              {/*  📚 Learn*/}
              {/*</button>*/}
              <button
                className={activeTab === 'calculator' ? 'tab-button-active' : 'tab-button'}
                onClick={() => setActiveTab('calculator')}
              >
                  Calculator
              </button>
              <button
                className={activeTab === 'optimizer' ? 'tab-button-active' : 'tab-button'}
                onClick={() => setActiveTab('optimizer')}
              >
                Optimizer
              </button>
              <button
                className={activeTab === 'visualize' ? 'tab-button-active' : 'tab-button'}
                onClick={() => setActiveTab('visualize')}
              >
                Visualize
              </button>
            </div>
          </nav>
      </header>


      <main className="flex-1 overflow-auto p-4 w-full">
        <div className="max-w-5xl mx-auto h-full">
          {/*{activeTab === 'tutorial' && <Tutorial />}*/}
          {activeTab === 'calculator' && <ISACalculator />}
          {activeTab === 'optimizer' && <OptimizationExplorer />}
          {activeTab === 'visualize' && <VisualizationDashboard />}
        </div>
      </main>

      <footer className="bg-gray-900 text-gray-50 p-4 text-center flex-shrink-0 text-sm font-medium">
          <p>built with <FontAwesomeIcon icon={faHeart} className="text-red-500 mx-1"/> by <a
              href="https://www.linkedin.com/in/sofia-baezzato" target="_blank">sofia</a> & <a
              href="https://www.claude.com/product/claude-code" target="_blank">claude</a></p>
      </footer>
    </div>
  )
}

export default App
