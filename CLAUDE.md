# International Standard Atmosphere Educational Platform

## Project Overview

This is an **educational platform** for learning atmospheric modeling that combines scientific accuracy with interactive exploration. The application implements the International Standard Atmosphere (ISA) model and compares it with simplified exponential models, teaching users about the trade-offs between model complexity and accuracy.

### Key Educational Features
- **Accurate ISA calculations** using the 8-layer atmospheric model (ISO 2533:1975 standard)
- **Exponential atmosphere models** with optimizable scale height (β) parameter
- **Interactive optimization** to find best-fit β for any altitude range
- **Visual learning tools** including 2D error heatmaps and comparison plots
- **Educational tutorials** explaining atmospheric physics and mathematical optimization

## Architecture

### Modular Design Pattern
The application uses a **modular architecture** with separate components:

**Core Python Modules:**
- `src/isa_calculator.py` - ISA atmosphere model implementation
- `src/exponential_models.py` - Exponential atmosphere models
- `src/optimizer.py` - Scale height optimization algorithms
- `src/visualizer.py` - Interactive visualizations and plotting
- `main.py` - Educational CLI interface
- `server.py` - FastAPI backend with REST endpoints

**React Frontend:**
- `frontend/src/App.jsx` - Main application with tab navigation
- `frontend/src/components/ISACalculator.jsx` - Interactive ISA calculator
- `frontend/src/components/OptimizationExplorer.jsx` - Scale height optimization
- `frontend/src/components/VisualizationDashboard.jsx` - Data visualization
- `frontend/src/components/Tutorial.jsx` - Educational content delivery

## Dependencies

### Backend Requirements
- **FastAPI ≥0.118.2** - Web framework for API endpoints
- **Matplotlib ≥3.10.7** - Visualization and plotting
- **NumPy ≥2.3.3** - Numerical computations
- **SciPy ≥1.16.2** - Optimization algorithms
- **Uvicorn ≥0.37.0** - ASGI server

### Frontend Requirements
- **React 19.1.1** - UI framework
- **Vite 7.1.7** - Build tool and dev server
- **Axios 1.12.2** - HTTP client for API communication
- **Recharts 3.2.1** - Data visualization components

## Development Commands

### Backend Development
```bash
# Install dependencies
uv sync

# Run CLI educational interface
python main.py

# Start FastAPI backend server
python server.py
# or
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Runs on port 5000 with API proxy to backend port 8000

# Build for production
npm run build

# Preview production build
npm run preview
```

### Full Stack Development
1. Start backend: `python server.py` (port 8000)
2. Start frontend: `cd frontend && npm run dev` (port 5000)
3. Access web app at `http://localhost:5000`

## API Endpoints

### ISA Calculations
- `POST /api/isa/calculate` - Calculate atmospheric parameters at given altitude
- Returns ISA results, error analysis, and exponential model comparison

### Optimization
- `POST /api/optimize` - Find optimal scale height for altitude range
- Returns optimization results and educational insights

### Visualization Data
- `POST /api/visualize/heatmap` - Generate β vs altitude error grid data
- `POST /api/visualize/comparison` - Multi-model atmospheric profile data

### Educational Content
- `GET /api/tutorial` - Structured tutorial content about atmospheric modeling

## Key Scientific Concepts

### International Standard Atmosphere (ISA)
- 8-layer atmospheric model covering 0-86km altitude
- Geopotential ↔ Geometric altitude conversion
- Layer-specific temperature lapse rates
- ISO 2533:1975 standard compliance

### Exponential Atmosphere Model
- Simple model: P(h) = P₀ × e^(-h/β)
- Scale height (β) parameter determines pressure decay rate
- Standard β = 8,000m, but can be optimized for specific ranges

### Optimization Insights
- **Low altitudes (0-15 km):** Optimal β ≈ 7,400m
- **Mid altitudes (0-30 km):** Optimal β ≈ 8,500m  
- **High altitudes (0-50 km):** Optimal β ≈ 9,200m

This demonstrates why no single exponential model can match the multi-layer ISA across all altitudes!

## Educational Modes

### CLI Interface (main.py)
1. **Tutorial Mode** - "What is an Exponential Atmosphere Model?" and "How Does Optimization Work?"
2. **Exploration Mode** - Optimize β for custom altitude ranges
3. **Visualization Mode** - Generate 2D error heatmaps and comparison plots
4. **Quick Calculator** - Immediate ISA calculations with exponential comparison

### Web Interface
- **ISA Calculator Tab** - Interactive atmospheric parameter calculation
- **Optimization Explorer Tab** - Visual scale height optimization
- **Visualization Dashboard Tab** - Interactive charts and heatmaps
- **Tutorial Tab** - Educational content with step-by-step explanations

## File Structure

```
International-Standard-Atmosphere/
├── src/
│   ├── isa_calculator.py      # Core ISA implementation
│   ├── exponential_models.py  # Exponential atmosphere models
│   ├── optimizer.py           # Scale height optimization
│   └── visualizer.py          # Visualization generation
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── App.jsx           # Main application
│   │   └── main.jsx          # Entry point
│   ├── package.json          # Frontend dependencies
│   └── vite.config.js        # Build configuration
├── main.py                   # Educational CLI interface
├── server.py                 # FastAPI backend
├── pyproject.toml            # Python dependencies
├── uv.lock                   # Dependency lock file
└── replit.md                 # Project specifications
```

## Testing

The application includes educational validation through:
- **Physical parameter verification** against known atmospheric data
- **Model comparison accuracy** between ISA and exponential models
- **Optimization convergence** testing with scipy algorithms
- **API endpoint validation** for frontend integration

## Standards Compliance

- **ISO 2533:1975** - International Standard Atmosphere
- **ICAO Standard Atmosphere** - Layer definitions and physical constants
- **Educational best practices** - Progressive learning and visual explanations

## Usage Notes

### For Educators
- Use CLI mode for step-by-step guided learning
- Web interface provides interactive exploration for students
- Visualizations can be exported for educational materials
- Tutorial content explains complex concepts in simple terms

### For Students
- Start with Tutorial mode to understand concepts
- Use Optimization Explorer to see how parameters affect accuracy
- Experiment with different altitude ranges in the calculator
- Visual heatmaps help understand mathematical relationships

### For Developers
- Modular architecture allows easy extension of atmospheric models
- API endpoints enable integration with other educational platforms
- Well-documented code with educational comments
- Clear separation between calculation, optimization, and visualization

## Communication Style

Preferred communication: Simple, everyday language suitable for educational contexts.

The platform emphasizes learning through exploration and visual understanding rather than complex mathematical derivations.
- the correct command to launch the backend is uv run .\server.py