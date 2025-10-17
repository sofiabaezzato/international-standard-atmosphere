# International Standard Atmosphere Model

Educational platform for atmospheric modeling. Implements ISA model and compares with exponential approximations.

## Overview

Calculates atmospheric parameters using International Standard Atmosphere (ISO 2533:1975) and optimizes exponential model parameters for different altitude ranges.

### NOTE: Web Interface (Cloud)
**Backend is deployed on free tier cloud server. Shuts down after inactivity. First API call may fail - be patient and retry after few seconds.**

## Data Sources and Calculations

### ISA Model
- **Standard**: ISO 2533:1975 International Standard Atmosphere
- **Layers**: 8 atmospheric layers (0-86 km)
- **Temperature profile**: Layer-specific lapse rates
- **Pressure calculation**: Hydrostatic equation with geopotential height conversion
- **Sea level conditions**: P₀ = 101325 Pa, T₀ = 288.15 K, g = 9.80665 m/s²

### Exponential Model
- **Formula**: P(h) = P₀ × exp(-h/β)
- **Standard β**: 8000 m (typical scale height)
- **Optimization**: Minimize RMSE between ISA and exponential models

### Key Assumptions
- Standard gravity at sea level
- Dry air composition
- No weather variations
- Geopotential height approximation for high altitudes

## Usage

### CLI Version
```bash
python main.py
```

Options:
1. Tutorial mode - atmospheric model explanations
2. Exploration mode - optimize β for custom altitude ranges  
3. Visualization mode - generate error heatmaps
4. Quick calculator - single altitude calculations

### Web Interface (Local)
```bash
# Start backend
python server.py

# Start frontend (separate terminal)
cd frontend
npm run dev
```

Access at `http://localhost:5000`

#### Web Screens

**ISA Calculator**
- Calculate atmospheric parameters at specific altitudes
- Compare ISA vs exponential model results
- Input: altitude, output: pressure, temperature, density

**Optimization Explorer**
- Find optimal β for altitude ranges
- Preset scenarios (troposphere, stratosphere, etc.)
- Results: optimal β, RMSE, comparison charts
- Export data as CSV

**Visualization Dashboard**
- 2D error heatmaps (β vs altitude)
- Multi-model atmospheric profiles
- Interactive parameter exploration

**Tutorial**
- Atmospheric physics explanations
- Mathematical model descriptions
- Optimization theory basics

## Key Findings

Optimal β values vary by altitude range:
- 0-15 km: ~7400 m
- 0-30 km: ~8500 m  
- 0-50 km: ~9200 m

Single exponential model cannot match ISA accuracy across all altitudes.

## Dependencies

Backend: FastAPI, NumPy, SciPy, Matplotlib
Frontend: React, Recharts, Axios

## File Structure

```
src/
├── isa_calculator.py    # ISA implementation
├── exponential_models.py # Exponential atmosphere models
├── optimizer.py         # β optimization algorithms
└── visualizer.py        # Chart generation

frontend/src/
├── components/          # React components
└── App.jsx             # Main application

main.py                 # CLI interface
server.py              # FastAPI backend
```