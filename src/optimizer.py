import numpy as np
from scipy.optimize import minimize

try:
    from .isa_calculator import ISACalculator
    from .exponential_models import ExponentialAtmosphere
except ImportError:
    from isa_calculator import ISACalculator
    from exponential_models import ExponentialAtmosphere

class ScaleHeightOptimizer:
    """Optimize scale height (beta) for exponential atmosphere model"""
    
    @staticmethod
    def objective_function(beta, altitudes, isa_pressures):
        """Sum of squared errors between exponential model and ISA"""
        errors_squared = 0
        for h, P_isa in zip(altitudes, isa_pressures):
            P_exp = ExponentialAtmosphere.calculate_pressure(h, beta[0])
            errors_squared += (P_exp - P_isa) ** 2
        return errors_squared
    
    @staticmethod
    def optimize_beta(h_min, h_max, num_points=100):
        """Find optimal scale height for given altitude range"""
        altitudes = np.linspace(h_min, h_max, num_points)
        
        isa_pressures = []
        for h in altitudes:
            results = ISACalculator.calculate_from_geometric(h)
            isa_pressures.append(results['pressure'])
        
        initial_beta = [8000]
        bounds = [(5000, 15000)]
        
        result = minimize(
            ScaleHeightOptimizer.objective_function,
            initial_beta,
            args=(altitudes, isa_pressures),
            method='L-BFGS-B',
            bounds=bounds
        )
        
        optimal_beta = result.x[0]
        
        rmse = np.sqrt(result.fun / len(altitudes))
        
        avg_pressure = np.mean(isa_pressures)
        rmse_percentage = (rmse / avg_pressure) * 100
        
        return {
            'optimal_beta': optimal_beta,
            'rmse': rmse,
            'rmse_percentage': rmse_percentage,
            'altitude_range': (h_min, h_max),
            'num_points': num_points
        }
    
    @staticmethod
    def analyze_optimization(h_min, h_max):
        """Detailed analysis of optimization results"""
        opt_results = ScaleHeightOptimizer.optimize_beta(h_min, h_max)
        optimal_beta = opt_results['optimal_beta']
        
        test_altitudes = [h_min, (h_min + h_max) / 2, h_max]
        comparisons = []
        
        for h in test_altitudes:
            isa_results = ISACalculator.calculate_from_geometric(h)
            exp_optimal = ExponentialAtmosphere.calculate_all(h, optimal_beta)
            exp_standard = ExponentialAtmosphere.calculate_all(h, 8000)
            
            comparisons.append({
                'altitude': h,
                'isa_pressure': isa_results['pressure'],
                'exp_optimal_pressure': exp_optimal['pressure'],
                'exp_standard_pressure': exp_standard['pressure'],
                'optimal_error_pct': ((exp_optimal['pressure'] - isa_results['pressure']) / isa_results['pressure'] * 100),
                'standard_error_pct': ((exp_standard['pressure'] - isa_results['pressure']) / isa_results['pressure'] * 100)
            })
        
        return {
            'optimization': opt_results,
            'comparisons': comparisons
        }
