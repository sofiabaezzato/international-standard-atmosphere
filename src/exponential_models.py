import math
import numpy as np

try:
    from .isa_calculator import ISACalculator
except ImportError:
    from isa_calculator import ISACalculator

class ExponentialAtmosphere:
    """Exponential atmosphere model: P(h) = P0 * exp(-h/H)"""
    
    STANDARD_SCALE_HEIGHT = 8000
    
    @staticmethod
    def calculate_pressure(h, scale_height):
        """Calculate pressure using exponential model"""
        return ISACalculator.P0 * math.exp(-h / scale_height)
    
    @staticmethod
    def calculate_density(h, scale_height):
        """Calculate density using exponential model (assuming isothermal)"""
        return ISACalculator.RHO0 * math.exp(-h / scale_height)
    
    @staticmethod
    def calculate_temperature(h, scale_height):
        """For exponential model, we assume constant temperature"""
        return ISACalculator.T0
    
    @staticmethod
    def calculate_all(h, scale_height):
        """Calculate all parameters for exponential model"""
        P = ExponentialAtmosphere.calculate_pressure(h, scale_height)
        rho = ExponentialAtmosphere.calculate_density(h, scale_height)
        T = ExponentialAtmosphere.calculate_temperature(h, scale_height)
        a = math.sqrt(ISACalculator.GAMMA * ISACalculator.R * T)
        
        return {
            'pressure': P,
            'density': rho,
            'temperature_K': T,
            'temperature_C': T - 273.15,
            'speed_of_sound': a,
            'scale_height': scale_height
        }
    
    @staticmethod
    def calculate_error_vs_isa(h, scale_height):
        """Calculate percentage error compared to ISA model"""
        isa_results = ISACalculator.calculate_from_geometric(h)
        exp_results = ExponentialAtmosphere.calculate_all(h, scale_height)
        
        errors = {
            'pressure_error_pct': ((exp_results['pressure'] - isa_results['pressure']) / isa_results['pressure'] * 100),
            'density_error_pct': ((exp_results['density'] - isa_results['density']) / isa_results['density'] * 100),
            'temperature_error_pct': ((exp_results['temperature_K'] - isa_results['temperature_K']) / isa_results['temperature_K'] * 100),
        }
        
        return errors
    
    @staticmethod
    def generate_error_grid(beta_range, altitude_range, num_beta=50, num_alt=100):
        """Generate 2D grid of errors for visualization"""
        betas = np.linspace(beta_range[0], beta_range[1], num_beta)
        altitudes = np.linspace(altitude_range[0], altitude_range[1], num_alt)
        
        pressure_errors = np.zeros((len(altitudes), len(betas)))
        
        for i, h in enumerate(altitudes):
            isa_results = ISACalculator.calculate_from_geometric(h)
            isa_pressure = isa_results['pressure']
            
            for j, beta in enumerate(betas):
                exp_pressure = ExponentialAtmosphere.calculate_pressure(h, beta)
                pressure_errors[i, j] = ((exp_pressure - isa_pressure) / isa_pressure * 100)
        
        return betas, altitudes, pressure_errors
