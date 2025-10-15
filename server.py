from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
from src import ISACalculator, ExponentialAtmosphere, ScaleHeightOptimizer

app = FastAPI(title="Atmosphere Model API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AltitudeRequest(BaseModel):
    altitude: float

class OptimizeRequest(BaseModel):
    min_altitude: float
    max_altitude: float
    num_points: Optional[int] = 100

class HeatmapRequest(BaseModel):
    min_altitude: float
    max_altitude: float
    min_beta: Optional[float] = 5000
    max_beta: Optional[float] = 12000
    num_beta: Optional[int] = 50
    num_alt: Optional[int] = 100

class ComparisonRequest(BaseModel):
    min_altitude: float
    max_altitude: float
    optimal_beta: float
    num_points: Optional[int] = 200

@app.get("/")
def read_root():
    return {
        "message": "Atmosphere Model Learning Tool API",
        "endpoints": {
            "isa_calculate": "/api/isa/calculate",
            "optimize": "/api/optimize",
            "heatmap": "/api/visualize/heatmap",
            "comparison": "/api/visualize/comparison",
            "tutorials": "/api/tutorial"
        }
    }

@app.post("/api/isa/calculate")
def calculate_isa(request: AltitudeRequest):
    try:
        altitude = request.altitude
        
        if altitude < 0:
            raise HTTPException(status_code=400, detail="Altitude must be non-negative")
        
        results = ISACalculator.calculate_from_geometric(altitude)
        errors = ISACalculator.calculate_error(altitude)
        
        exp_standard = ExponentialAtmosphere.calculate_all(altitude, 8000)
        exp_error = ((exp_standard['pressure'] - results['pressure']) / results['pressure'] * 100)
        
        return {
            "isa": {
                "geometric_altitude": results['geometric_altitude'],
                "geopotential_altitude": results['geopotential_altitude'],
                "temperature_K": results['temperature_K'],
                "temperature_C": results['temperature_C'],
                "pressure": results['pressure'],
                "density": results['density'],
                "speed_of_sound": results['speed_of_sound'],
                "pressure_ratio": results['pressure_ratio'],
                "density_ratio": results['density_ratio']
            },
            "errors": {
                "altitude_difference_m": errors['altitude_difference_m'],
                "altitude_error_pct": errors['altitude_error_pct'],
                "temperature_error_pct": errors['temperature_error_pct'],
                "pressure_error_pct": errors['pressure_error_pct'],
                "density_error_pct": errors['density_error_pct']
            },
            "exponential_comparison": {
                "pressure": exp_standard['pressure'],
                "error_pct": exp_error
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize")
def optimize_beta(request: OptimizeRequest):
    try:
        h_min = request.min_altitude
        h_max = request.max_altitude
        
        if h_min < 0 or h_max < 0:
            raise HTTPException(status_code=400, detail="Altitudes must be non-negative")
        
        if h_min >= h_max:
            raise HTTPException(status_code=400, detail="Min altitude must be less than max altitude")
        
        analysis = ScaleHeightOptimizer.analyze_optimization(h_min, h_max)
        opt_results = analysis['optimization']
        
        comparison_data = []
        for comp in analysis['comparisons']:
            comparison_data.append({
                "altitude": comp['altitude'],
                "altitude_km": comp['altitude'] / 1000,
                "isa_pressure": comp['isa_pressure'],
                "exp_optimal_pressure": comp['exp_optimal_pressure'],
                "exp_standard_pressure": comp['exp_standard_pressure'],
                "optimal_error_pct": comp['optimal_error_pct'],
                "standard_error_pct": comp['standard_error_pct']
            })
        
        insights = []
        optimal_beta = opt_results['optimal_beta']
        diff_from_standard = optimal_beta - 8000
        
        if h_max <= 15000:
            insights.append(f"For low altitudes (0-15 km), optimal β ≈ {optimal_beta:.0f}m is lower than standard 8,000m")
            insights.append("This is because the troposphere has a temperature gradient causing faster pressure decrease")
        elif h_max <= 30000:
            insights.append(f"For mid altitudes (0-30 km), optimal β ≈ {optimal_beta:.0f}m is close to standard")
            insights.append("This balances tropospheric cooling with stratospheric isothermal regions")
        else:
            insights.append(f"For high altitudes (0-{h_max/1000:.0f} km), optimal β ≈ {optimal_beta:.0f}m is higher than standard")
            insights.append("Stratospheric warming affects the average temperature profile")
        
        if abs(diff_from_standard) < 500:
            insights.append(f"Optimal β is very close to standard (difference: {diff_from_standard:+.0f}m)")
        elif diff_from_standard > 0:
            insights.append(f"Optimal β is {diff_from_standard:.0f}m higher - standard would underestimate pressures")
        else:
            insights.append(f"Optimal β is {abs(diff_from_standard):.0f}m lower - standard would overestimate pressures")
        
        return {
            "optimization": {
                "optimal_beta": opt_results['optimal_beta'],
                "rmse": opt_results['rmse'],
                "rmse_percentage": opt_results['rmse_percentage'],
                "altitude_range_km": [h_min/1000, h_max/1000]
            },
            "comparisons": comparison_data,
            "insights": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/visualize/heatmap")
def generate_heatmap_data(request: HeatmapRequest):
    try:
        betas, altitudes, errors = ExponentialAtmosphere.generate_error_grid(
            (request.min_beta, request.max_beta),
            (request.min_altitude, request.max_altitude),
            num_beta=request.num_beta or 50,
            num_alt=request.num_alt or 100
        )
        
        return {
            "betas": betas.tolist(),
            "altitudes": (altitudes / 1000).tolist(),
            "errors": errors.tolist(),
            "altitude_range_km": [request.min_altitude/1000, request.max_altitude/1000]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/visualize/comparison")
def generate_comparison_data(request: ComparisonRequest):
    try:
        altitudes = np.linspace(request.min_altitude, request.max_altitude, request.num_points or 200)
        
        isa_data = []
        exp_optimal_data = []
        exp_standard_data = []
        
        for h in altitudes:
            isa = ISACalculator.calculate_from_geometric(h)
            exp_opt = ExponentialAtmosphere.calculate_all(h, request.optimal_beta)
            exp_std = ExponentialAtmosphere.calculate_all(h, 8000)
            
            isa_data.append({
                "altitude_km": h / 1000,
                "altitude_m": h,
                "pressure": isa['pressure'],
                "temperature": isa['temperature_K'],
                "density": isa['density']
            })
            
            exp_optimal_data.append({
                "altitude_km": h / 1000,
                "altitude_m": h,
                "pressure": exp_opt['pressure'],
                "density": exp_opt['density']
            })
            
            exp_standard_data.append({
                "altitude_km": h / 1000,
                "altitude_m": h,
                "pressure": exp_std['pressure'],
                "density": exp_std['density']
            })
        
        pressure_errors_optimal = [
            ((exp['pressure'] - isa['pressure']) / isa['pressure'] * 100)
            for exp, isa in zip(exp_optimal_data, isa_data)
        ]
        
        pressure_errors_standard = [
            ((exp['pressure'] - isa['pressure']) / isa['pressure'] * 100)
            for exp, isa in zip(exp_standard_data, isa_data)
        ]
        
        return {
            "isa": isa_data,
            "exponential_optimal": exp_optimal_data,
            "exponential_standard": exp_standard_data,
            "errors_optimal": pressure_errors_optimal,
            "errors_standard": pressure_errors_standard,
            "optimal_beta": request.optimal_beta
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tutorial")
def get_tutorials():
    return {
        "exponential_model": {
            "title": "What is an Exponential Atmosphere Model?",
            "sections": [
                {
                    "heading": "The Concept",
                    "content": "The exponential model is a SIMPLIFIED way to describe how air pressure and density decrease with altitude. It uses a single parameter called SCALE HEIGHT (β)."
                },
                {
                    "heading": "The Formula",
                    "content": "P(h) = P₀ × e^(-h/β)",
                    "variables": {
                        "P(h)": "Pressure at altitude h",
                        "P₀": "Sea level pressure (101,325 Pa)",
                        "h": "Altitude (meters)",
                        "β": "Scale height (meters) - THE KEY PARAMETER!"
                    }
                },
                {
                    "heading": "What is Scale Height (β)?",
                    "content": "Scale height tells you how 'quickly' the atmosphere thins out. Larger β means atmosphere thins SLOWLY. Smaller β means atmosphere thins QUICKLY. Standard value is β = 8,000 meters."
                }
            ]
        },
        "optimization": {
            "title": "How Does Optimization Work?",
            "sections": [
                {
                    "heading": "The Goal",
                    "content": "Find the β value that makes the exponential model as close as possible to the accurate ISA model."
                },
                {
                    "heading": "The Method",
                    "content": "We use Least Squares Optimization to minimize the sum of squared errors between the exponential model and ISA pressures."
                },
                {
                    "heading": "Key Insight",
                    "content": "NO single β value gives 0% error at ALL altitudes! This shows why the multi-layer ISA model is more accurate than a simple exponential model."
                }
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
