"""
Scale Height Optimization for Exponential Atmosphere Models

This module implements advanced optimization algorithms to find optimal scale height
parameters (β) for exponential atmosphere models. The optimization process minimizes
the error between exponential model predictions and International Standard Atmosphere
(ISA) reference data over specified altitude ranges.

Optimization Problem Formulation:
Given an altitude range [h_min, h_max], find the scale height β that minimizes:

Objective Function: f(β) = Σ[P_exp(h_i, β) - P_ISA(h_i)]²

Where:
- P_exp(h_i, β) = P₀ × exp(-h_i/β) is the exponential model pressure
- P_ISA(h_i) is the ISA reference pressure at altitude h_i
- The sum is over all altitude sample points in the range

Mathematical Approach:
This is a non-linear least squares optimization problem with a single parameter β.
The objective function is smooth and convex for typical atmospheric conditions,
making gradient-based methods highly effective.

Algorithm Selection:
L-BFGS-B (Limited-memory Broyden-Fletcher-Goldfarb-Shanno with bounds) is used because:
1. Efficient for single-parameter optimization
2. Handles bound constraints (β must be physically reasonable)
3. Uses gradient information for fast convergence
4. Memory-efficient for large datasets
5. Robust numerical implementation in SciPy

Error Metrics:
- Root Mean Square Error (RMSE): √(Σ(P_exp - P_ISA)²/n)
- RMSE Percentage: (RMSE / mean(P_ISA)) × 100%

Applications:
- Model parameter tuning for specific altitude ranges
- Accuracy assessment of exponential approximations
- Trade-off analysis between model simplicity and precision
- Educational demonstration of optimization principles

Computational Complexity:
- Time: O(n×k) where n = number of altitude points, k = optimization iterations
- Space: O(n) for storing altitude and pressure arrays
- Typical performance: <1 second for 100 points, 10-50 iterations
"""

import numpy as np
from scipy.optimize import minimize

try:
    from .isa_calculator import ISACalculator
    from .exponential_models import ExponentialAtmosphere
except ImportError:
    from isa_calculator import ISACalculator
    from exponential_models import ExponentialAtmosphere

class ScaleHeightOptimizer:
    """
    Scale Height Optimization Engine for Exponential Atmosphere Models
    
    This class provides sophisticated optimization algorithms to determine optimal
    scale height parameters for exponential atmosphere models. It implements both
    single-parameter optimization and comprehensive analysis tools for model
    evaluation and comparison.
    
    The optimizer uses advanced numerical methods to solve the non-linear least
    squares problem of fitting exponential pressure decay to ISA reference data.
    """
    
    @staticmethod
    def objective_function(beta, altitudes, isa_pressures):
        """
        Objective function for scale height optimization using sum of squared errors.
        
        This function implements the core mathematical objective that the optimization
        algorithm seeks to minimize. It calculates the sum of squared differences
        between exponential model predictions and ISA reference pressures across
        all altitude points in the optimization dataset.
        
        Mathematical Formulation:
        f(β) = Σᵢ [P_exp(hᵢ, β) - P_ISA(hᵢ)]²
        
        Where:
        - β is the scale height parameter being optimized
        - hᵢ are the altitude sample points
        - P_exp(hᵢ, β) = P₀ × exp(-hᵢ/β) is the exponential model prediction
        - P_ISA(hᵢ) is the ISA reference pressure at altitude hᵢ
        
        Error Metric Choice - Sum of Squared Errors (SSE):
        
        Advantages:
        1. Smooth and differentiable (enables gradient-based optimization)
        2. Convex function for exponential models (single global minimum)
        3. Heavily penalizes large errors (quadratic penalty)
        4. Standard choice for least-squares fitting
        5. Efficient computation and numerical stability
        
        Disadvantages:
        1. Sensitive to pressure magnitude (biases toward low altitudes)
        2. Not scale-invariant (results depend on pressure units)
        3. Can be dominated by outliers or extreme values
        
        Alternative Error Metrics:
        - Root Mean Square Error (RMSE): √(SSE/n) - normalized version
        - Mean Absolute Error (MAE): Σ|P_exp - P_ISA|/n - less sensitive to outliers
        - Percentage Error: Σ[(P_exp - P_ISA)/P_ISA]² - scale-invariant
        
        Computational Considerations:
        - Vectorized operations possible but loop used for clarity
        - Numerical precision: Uses 64-bit floating point arithmetic
        - Overflow protection: Exponential calculations bounded by input constraints
        
        Args:
            beta (array): Scale height parameter [m] (SciPy optimization format)
            altitudes (array): Altitude sample points [m]
            isa_pressures (array): ISA reference pressures [Pa]
            
        Returns:
            float: Sum of squared errors between exponential model and ISA [Pa²]
            
        Note:
            The beta parameter is passed as an array by SciPy's minimize function,
            hence beta[0] is used to extract the scalar value. This interface
            enables extension to multi-parameter optimization if needed.
        """
        # Initialize cumulative sum of squared errors
        errors_squared = 0
        
        # Extract scalar beta value from optimization array format
        # SciPy's minimize passes parameters as arrays for generality
        beta_value = beta[0]
        
        # Calculate squared errors for each altitude point
        for h, P_isa in zip(altitudes, isa_pressures):
            # Calculate exponential model pressure at this altitude
            P_exp = ExponentialAtmosphere.calculate_pressure(h, beta_value)
            
            # Compute squared error: (predicted - reference)²
            # Squaring ensures positive contributions and penalizes large errors
            error_squared = (P_exp - P_isa) ** 2
            
            # Accumulate total squared error
            errors_squared += error_squared
        
        return errors_squared
    
    @staticmethod
    def optimize_beta(h_min, h_max, num_points=100):
        """
        Find optimal scale height parameter for exponential atmosphere model.
        
        This function performs comprehensive scale height optimization for a specified
        altitude range using advanced numerical methods. It generates a reference
        dataset from ISA calculations and then applies L-BFGS-B optimization to
        find the β value that minimizes prediction errors.
        
        Optimization Process:
        1. Generate uniformly-spaced altitude samples across [h_min, h_max]
        2. Calculate ISA reference pressures for all altitude points
        3. Set up optimization problem with initial guess and bounds
        4. Execute L-BFGS-B algorithm to minimize sum of squared errors
        5. Calculate performance metrics and format results
        
        Algorithm Details - L-BFGS-B:
        
        L-BFGS-B (Limited-memory Broyden-Fletcher-Goldfarb-Shanno with Bounds):
        - Quasi-Newton method using gradient information
        - Limited memory approximation for computational efficiency
        - Handles bound constraints on optimization variables
        - Superlinear convergence for smooth objective functions
        - Memory requirement: O(m) where m << n (typically m = 10-20)
        
        Convergence Criteria:
        - Gradient norm: ||∇f|| < 1e-5 (default SciPy tolerance)
        - Function value change: |f(x_{k+1}) - f(x_k)| < factr * ε
        - Maximum iterations: 15000 (SciPy default)
        
        Sampling Strategy:
        Uniform altitude spacing ensures:
        1. Equal representation across altitude range
        2. Predictable computational cost
        3. Consistent optimization behavior
        4. Fair weighting of all altitude regions
        
        Parameter Bounds Justification:
        - Lower bound (5000m): Prevents unphysically small scale heights
        - Upper bound (15000m): Prevents unrealistic atmospheric "thickness"
        - Range covers all practical exponential atmosphere applications
        - Ensures numerical stability and convergence
        
        Error Metrics:
        - RMSE: Root Mean Square Error in absolute pressure units [Pa]
        - RMSE%: Percentage RMSE relative to mean ISA pressure [%]
        
        Args:
            h_min (float): Minimum altitude of optimization range [m]
            h_max (float): Maximum altitude of optimization range [m]
            num_points (int): Number of altitude samples for optimization (default: 100)
            
        Returns:
            dict: Comprehensive optimization results containing:
                - optimal_beta [m]: Optimized scale height parameter
                - rmse [Pa]: Root Mean Square Error in pressure
                - rmse_percentage [%]: Relative RMSE as percentage
                - altitude_range [tuple]: (h_min, h_max) optimization range
                - num_points [int]: Number of data points used
                
        Computational Performance:
        - Typical execution time: 10-100 ms for 100 points
        - Memory usage: O(num_points) for arrays
        - Convergence: Usually 10-50 L-BFGS-B iterations
        
        Optimization Quality Indicators:
        - RMSE% < 1%: Excellent fit for most applications
        - RMSE% 1-5%: Good fit for preliminary calculations
        - RMSE% > 5%: Poor fit, consider different model or altitude range
        
        Example Usage:
            # Optimize for troposphere (0-11 km)
            result = ScaleHeightOptimizer.optimize_beta(0, 11000)
            print(f"Optimal β: {result['optimal_beta']:.0f} m")
            print(f"RMSE: {result['rmse_percentage']:.2f}%")
        """
        # Step 1: Generate uniformly-spaced altitude array
        # Linear spacing ensures equal weight to all altitude regions
        altitudes = np.linspace(h_min, h_max, num_points)
        
        # Step 2: Calculate ISA reference pressures for optimization dataset
        # These serve as "ground truth" target values for the optimization
        isa_pressures = []
        for h in altitudes:
            # Use full ISA model including geopotential altitude correction
            results = ISACalculator.calculate_from_geometric(h)
            isa_pressures.append(results['pressure'])
        
        # Step 3: Set up optimization problem parameters
        # Initial guess: 8000m (typical atmospheric scale height)
        initial_beta = [8000]
        
        # Parameter bounds: physically reasonable scale height range
        # Lower bound: 5000m (prevents unphysically thin atmosphere)
        # Upper bound: 15000m (prevents unrealistic thick atmosphere)
        bounds = [(5000, 15000)]
        
        # Step 4: Execute L-BFGS-B optimization algorithm
        result = minimize(
            ScaleHeightOptimizer.objective_function,    # Objective function to minimize
            initial_beta,                               # Initial parameter guess
            args=(altitudes, isa_pressures),           # Additional arguments to objective
            method='L-BFGS-B',                         # Optimization algorithm
            bounds=bounds                              # Parameter constraints
        )
        
        # Step 5: Extract optimal parameter and calculate performance metrics
        optimal_beta = result.x[0]  # Extract optimized scale height
        
        # Calculate Root Mean Square Error (RMSE)
        # RMSE = √(SSE/n) where SSE is the minimized objective function value
        rmse = np.sqrt(result.fun / len(altitudes))
        
        # Calculate percentage RMSE relative to mean pressure
        # This provides scale-invariant error assessment
        avg_pressure = np.mean(isa_pressures)
        rmse_percentage = (rmse / avg_pressure) * 100
        
        # Step 6: Format comprehensive results dictionary
        return {
            'optimal_beta': optimal_beta,               # Optimized scale height [m]
            'rmse': rmse,                              # Absolute RMSE [Pa]
            'rmse_percentage': rmse_percentage,        # Relative RMSE [%]
            'altitude_range': (h_min, h_max),         # Optimization altitude range [m]
            'num_points': num_points                   # Number of data points used
        }
    
    @staticmethod
    def analyze_optimization(h_min, h_max, num_chart_points=50):
        """
        Comprehensive analysis and comparison of optimization results.
        
        This function provides detailed analysis of scale height optimization
        performance by comparing optimized and standard exponential models
        against ISA reference data. It generates point-by-point comparisons
        suitable for visualization and quantitative assessment.
        
        Analysis Framework:
        1. Perform scale height optimization for the specified altitude range
        2. Generate detailed comparison dataset at higher resolution
        3. Calculate atmospheric properties for three models:
           - ISA (International Standard Atmosphere) - reference
           - Optimized exponential model - β optimized for this range
           - Standard exponential model - β = 8000m (typical value)
        4. Compute percentage errors for model comparison
        
        Comparison Methodology:
        The analysis uses independent altitude sampling for visualization
        (num_chart_points) that differs from optimization sampling. This
        approach provides:
        1. Model validation on unseen data points
        2. Higher resolution for smooth plotting
        3. Assessment of interpolation accuracy
        4. Detection of systematic errors or oscillations
        
        Error Calculation:
        Percentage Error = (Model_Pressure - ISA_Pressure) / ISA_Pressure × 100%
        
        Positive errors: Model over-predicts pressure
        Negative errors: Model under-predicts pressure
        
        Model Comparison Insights:
        - Optimal model should show smaller errors than standard model
        - Error patterns reveal altitude-dependent model limitations
        - Standard model performance indicates need for optimization
        - Error magnitude suggests model suitability for applications
        
        Visualization Applications:
        The returned data structure supports various plot types:
        1. Pressure vs altitude curves for all three models
        2. Error vs altitude plots showing optimization benefit
        3. Comparison of optimal vs standard model performance
        4. Statistical analysis of error distributions
        
        Args:
            h_min (float): Minimum altitude of analysis range [m]
            h_max (float): Maximum altitude of analysis range [m]
            num_chart_points (int): Number of points for detailed comparison (default: 50)
            
        Returns:
            dict: Comprehensive analysis results containing:
                - optimization: Complete optimization results from optimize_beta()
                - comparisons: List of dictionaries, each containing:
                    - altitude [m]: Sample altitude point
                    - isa_pressure [Pa]: ISA reference pressure
                    - exp_optimal_pressure [Pa]: Optimized exponential pressure
                    - exp_standard_pressure [Pa]: Standard exponential pressure  
                    - optimal_error_pct [%]: Optimized model error
                    - standard_error_pct [%]: Standard model error
                    
        Data Structure:
        The comparisons list contains one dictionary per altitude point,
        enabling easy extraction for plotting and statistical analysis.
        Each comparison point includes both absolute values and relative errors.
        
        Performance Metrics:
        Users can derive additional statistics from the comparison data:
        - Maximum errors: max(|optimal_error_pct|), max(|standard_error_pct|)
        - RMS errors: √(mean(error²)) for both models
        - Error improvement: standard_error - optimal_error
        - Error standard deviation: measure of error consistency
        
        Example Usage:
            # Analyze troposphere optimization
            analysis = ScaleHeightOptimizer.analyze_optimization(0, 11000)
            optimal_beta = analysis['optimization']['optimal_beta']
            errors = [pt['optimal_error_pct'] for pt in analysis['comparisons']]
            print(f"Optimal β: {optimal_beta:.0f} m")
            print(f"Max error: {max(abs(e) for e in errors):.2f}%")
        """
        # Step 1: Perform scale height optimization for the specified range
        opt_results = ScaleHeightOptimizer.optimize_beta(h_min, h_max)
        optimal_beta = opt_results['optimal_beta']
        
        # Step 2: Generate high-resolution altitude array for detailed analysis
        # This provides finer sampling than optimization for smooth visualization
        test_altitudes = np.linspace(h_min, h_max, num_chart_points)
        
        # Step 3: Calculate comprehensive comparison data
        comparisons = []
        
        for h in test_altitudes:
            # Calculate ISA reference values (ground truth)
            isa_results = ISACalculator.calculate_from_geometric(h)
            
            # Calculate optimized exponential model values
            exp_optimal = ExponentialAtmosphere.calculate_all(h, optimal_beta)
            
            # Calculate standard exponential model values (β = 8000m)
            exp_standard = ExponentialAtmosphere.calculate_all(h, 8000)
            
            # Compute percentage errors for both exponential models
            optimal_error_pct = ((exp_optimal['pressure'] - isa_results['pressure']) / isa_results['pressure'] * 100)
            standard_error_pct = ((exp_standard['pressure'] - isa_results['pressure']) / isa_results['pressure'] * 100)
            
            # Store comprehensive comparison data for this altitude
            comparisons.append({
                'altitude': h,                                    # Sample altitude [m]
                'isa_pressure': isa_results['pressure'],        # ISA reference [Pa]
                'exp_optimal_pressure': exp_optimal['pressure'], # Optimized model [Pa]
                'exp_standard_pressure': exp_standard['pressure'], # Standard model [Pa]
                'optimal_error_pct': optimal_error_pct,         # Optimized error [%]
                'standard_error_pct': standard_error_pct        # Standard error [%]
            })
        
        # Step 4: Return comprehensive analysis results
        return {
            'optimization': opt_results,    # Complete optimization results
            'comparisons': comparisons      # Point-by-point comparison data
        }
