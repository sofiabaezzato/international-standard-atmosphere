"""
Exponential Atmosphere Models

This module implements simplified exponential atmospheric models that approximate
pressure and density decay with altitude using exponential functions. These models
are commonly used in aerospace engineering for preliminary calculations and
educational purposes due to their mathematical simplicity.

Theoretical Foundation:
The exponential atmosphere model assumes:
1. Isothermal atmosphere (constant temperature)
2. Hydrostatic equilibrium: dP = -ρg dh
3. Ideal gas law: P = ρRT
4. Exponential pressure decay: P(h) = P₀ × exp(-h/β)

Mathematical Derivation:
Starting from hydrostatic equilibrium in isothermal conditions:
dP/dh = -ρg = -Pg/(RT)

Rearranging: dP/P = -g/(RT) dh

Integration: ln(P/P₀) = -gh/(RT)

Therefore: P(h) = P₀ × exp(-h/β)

Where β = RT/g is the scale height parameter representing the altitude at which
pressure decreases by a factor of e (≈2.718).

Scale Height Physical Meaning:
- β represents atmospheric "thickness"
- Larger β → thicker atmosphere, slower pressure decay
- Smaller β → thinner atmosphere, faster pressure decay
- Standard value: β ≈ 8000-8500 m for Earth's atmosphere

Applications:
- Rocket trajectory analysis
- Atmospheric entry calculations
- Educational atmospheric modeling
- Preliminary aerospace design

Limitations:
- Ignores temperature variation with altitude
- Single-parameter model cannot capture complex atmospheric structure
- Less accurate than multi-layer models like ISA
- Best suited for limited altitude ranges
"""

import math
import numpy as np

try:
    from .isa_calculator import ISACalculator
except ImportError:
    from isa_calculator import ISACalculator

class ExponentialAtmosphere:
    """
    Exponential Atmosphere Model Implementation
    
    Provides methods to calculate atmospheric properties using the simplified
    exponential model P(h) = P₀ × exp(-h/β), where β is the scale height parameter.
    
    The model assumes isothermal conditions and exponential pressure/density decay,
    making it mathematically tractable for analytical solutions in aerospace
    engineering applications.
    """
    
    # Standard scale height value commonly used in atmospheric modeling
    # This represents a typical value for Earth's atmosphere
    STANDARD_SCALE_HEIGHT = 8500  # meters
    
    @staticmethod
    def calculate_pressure(h, scale_height):
        """
        Calculate atmospheric pressure using exponential decay model.
        
        Implements the fundamental exponential atmosphere equation:
        P(h) = P₀ × exp(-h/β)
        
        Mathematical Foundation:
        This equation results from integrating the hydrostatic equation
        under isothermal conditions. The exponential decay reflects the
        balance between gravitational compression and thermal expansion.
        
        Physical Interpretation:
        - At h = 0: P = P₀ (sea level pressure)
        - At h = β: P = P₀/e ≈ 0.368 × P₀ (36.8% of sea level pressure)
        - At h = 2β: P = P₀/e² ≈ 0.135 × P₀ (13.5% of sea level pressure)
        
        Args:
            h (float): Geometric altitude above sea level [m]
            scale_height (float): Scale height parameter β [m]
            
        Returns:
            float: Atmospheric pressure [Pa]
            
        Example:
            At 8500m altitude with β = 8500m:
            P = 101325 × exp(-8500/8500) = 101325 × exp(-1) ≈ 37,270 Pa
        """
        return ISACalculator.P0 * math.exp(-h / scale_height)
    
    @staticmethod
    def calculate_density(h, scale_height):
        """
        Calculate atmospheric density using exponential decay model.
        
        Under isothermal conditions with constant temperature T₀, the ideal gas law
        P = ρRT combined with exponential pressure decay yields exponential density decay:
        ρ(h) = ρ₀ × exp(-h/β)
        
        Theoretical Justification:
        Since P(h) = P₀ × exp(-h/β) and T(h) = T₀ = constant
        From P = ρRT: ρ = P/(RT)
        Therefore: ρ(h) = P(h)/(RT₀) = [P₀ × exp(-h/β)]/(RT₀) = ρ₀ × exp(-h/β)
        
        Where ρ₀ = P₀/(RT₀) is the sea level density.
        
        Physical Meaning:
        The density follows the same exponential decay as pressure because
        temperature is assumed constant. This assumption is reasonable for
        limited altitude ranges but breaks down over large altitude spans
        where temperature varies significantly.
        
        Args:
            h (float): Geometric altitude above sea level [m]
            scale_height (float): Scale height parameter β [m]
            
        Returns:
            float: Atmospheric density [kg/m³]
            
        Limitation:
            This calculation assumes isothermal conditions, which is an
            approximation. Real atmospheric density varies due to both
            pressure and temperature changes with altitude.
        """
        return ISACalculator.RHO0 * math.exp(-h / scale_height)
    
    @staticmethod
    def calculate_temperature(h, scale_height):
        """
        Return constant temperature for exponential atmosphere model.
        
        The exponential atmosphere model assumes isothermal conditions,
        meaning temperature remains constant at all altitudes. This is
        the fundamental simplifying assumption that enables the exponential
        pressure/density relationships.
        
        Isothermal Assumption Justification:
        While unrealistic for large altitude ranges, the isothermal assumption:
        1. Enables analytical solutions for many aerospace problems
        2. Provides reasonable accuracy over limited altitude ranges
        3. Simplifies mathematical analysis significantly
        4. Serves as a useful first-order approximation
        
        Real Atmosphere vs Model:
        - Real atmosphere: Temperature varies significantly with altitude
        - Exponential model: Temperature = constant = T₀ = 288.15 K
        - Trade-off: Mathematical simplicity vs physical realism
        
        Args:
            h (float): Geometric altitude [m] (not used, included for interface consistency)
            scale_height (float): Scale height parameter [m] (not used)
            
        Returns:
            float: Constant temperature T₀ = 288.15 K
            
        Note:
            The altitude and scale_height parameters are not used in the calculation
            but are included to maintain consistent function signatures across
            different atmospheric models.
        """
        return ISACalculator.T0
    
    @staticmethod
    def calculate_all(h, scale_height):
        """
        Calculate complete atmospheric state using exponential model.
        
        This function provides a comprehensive calculation of all atmospheric
        properties at a given altitude using the exponential atmosphere model.
        It serves as the main interface for obtaining complete atmospheric
        state information.
        
        Calculation Sequence:
        1. Calculate pressure using exponential decay: P = P₀ × exp(-h/β)
        2. Calculate density using exponential decay: ρ = ρ₀ × exp(-h/β)
        3. Set temperature to constant value: T = T₀
        4. Calculate speed of sound using thermodynamic relation: a = √(γRT)
        
        Speed of Sound Calculation:
        The acoustic velocity is calculated using the thermodynamic relation
        for ideal gases: a = √(γRT), where:
        - γ = ratio of specific heats (1.4 for air)
        - R = specific gas constant for air (287.05 J/(kg·K))
        - T = temperature (constant T₀ in this model)
        
        Args:
            h (float): Geometric altitude above sea level [m]
            scale_height (float): Scale height parameter β [m]
            
        Returns:
            dict: Complete atmospheric properties containing:
                - pressure [Pa]: Atmospheric pressure
                - density [kg/m³]: Air density
                - temperature_K [K]: Absolute temperature (constant)
                - temperature_C [°C]: Celsius temperature (constant)
                - speed_of_sound [m/s]: Acoustic velocity (constant)
                - scale_height [m]: Scale height parameter used
                
        Output Format:
        The results are returned in a dictionary format consistent with
        ISA calculator outputs, enabling easy comparison between different
        atmospheric models.
        """
        # Calculate primary atmospheric properties using exponential model
        P = ExponentialAtmosphere.calculate_pressure(h, scale_height)
        rho = ExponentialAtmosphere.calculate_density(h, scale_height)
        T = ExponentialAtmosphere.calculate_temperature(h, scale_height)
        
        # Calculate speed of sound using thermodynamic relation
        # a = √(γRT) where γ is ratio of specific heats, R is gas constant
        a = math.sqrt(ISACalculator.GAMMA * ISACalculator.R * T)
        
        # Format results into comprehensive output dictionary
        return {
            'pressure': P,                          # Atmospheric pressure [Pa]
            'density': rho,                         # Air density [kg/m³]
            'temperature_K': T,                     # Absolute temperature [K]
            'temperature_C': T - 273.15,           # Celsius temperature [°C]
            'speed_of_sound': a,                   # Acoustic velocity [m/s]
            'scale_height': scale_height           # Scale height parameter [m]
        }
    
    @staticmethod
    def calculate_error_vs_isa(h, scale_height):
        """
        Calculate percentage errors between exponential model and ISA reference.
        
        This function quantifies the accuracy of the exponential atmosphere model
        by comparing its predictions with the International Standard Atmosphere
        (ISA) at a specific altitude and scale height. The ISA serves as the
        reference standard for atmospheric modeling.
        
        Error Calculation Method:
        For each atmospheric property:
        Error [%] = (Exponential_Value - ISA_Value) / ISA_Value × 100
        
        Positive errors indicate exponential model over-predicts
        Negative errors indicate exponential model under-predicts
        
        Error Sources:
        1. Isothermal assumption vs ISA temperature lapse rates
        2. Single exponential decay vs multi-layer atmospheric structure
        3. Constant scale height vs varying atmospheric properties
        
        Typical Error Patterns:
        - Pressure errors: Generally increase with altitude and scale height mismatch
        - Density errors: Follow pressure errors due to isothermal assumption
        - Temperature errors: Large and systematic due to constant vs variable temperature
        
        Args:
            h (float): Geometric altitude above sea level [m]
            scale_height (float): Scale height parameter β [m]
            
        Returns:
            dict: Percentage errors for each atmospheric property:
                - pressure_error_pct [%]: Pressure prediction error
                - density_error_pct [%]: Density prediction error
                - temperature_error_pct [%]: Temperature prediction error
                
        Application:
        These errors help determine:
        1. Optimal scale height for specific altitude ranges
        2. Altitude limits where exponential model remains acceptable
        3. Trade-offs between model simplicity and accuracy
        """
        # Calculate ISA reference values (ground truth)
        isa_results = ISACalculator.calculate_from_geometric(h)
        
        # Calculate exponential model predictions
        exp_results = ExponentialAtmosphere.calculate_all(h, scale_height)
        
        # Compute percentage errors using ISA as reference
        # Error formula: (predicted - reference) / reference × 100%
        errors = {
            'pressure_error_pct': ((exp_results['pressure'] - isa_results['pressure']) / isa_results['pressure'] * 100),
            'density_error_pct': ((exp_results['density'] - isa_results['density']) / isa_results['density'] * 100),
            'temperature_error_pct': ((exp_results['temperature_K'] - isa_results['temperature_K']) / isa_results['temperature_K'] * 100),
        }
        
        return errors
    
    @staticmethod
    def generate_error_grid(beta_range, altitude_range, num_beta=50, num_alt=100):
        """
        Generate 2D error grid for visualization of exponential model accuracy.
        
        This function creates a comprehensive error surface showing how exponential
        model accuracy varies with both scale height (β) and altitude. The resulting
        grid enables visualization of optimal β values and accuracy trade-offs across
        different altitude ranges.
        
        Grid Generation Process:
        1. Create linearly-spaced arrays for β values and altitudes
        2. For each altitude: calculate ISA reference pressure
        3. For each (altitude, β) combination: calculate exponential pressure
        4. Compute percentage error matrix: (P_exp - P_isa) / P_isa × 100
        
        Mathematical Framework:
        The error surface E(h,β) represents:
        E(h,β) = [P₀×exp(-h/β) - P_ISA(h)] / P_ISA(h) × 100%
        
        Where:
        - h varies across altitude_range
        - β varies across beta_range  
        - P_ISA(h) is the ISA reference pressure at altitude h
        
        Visualization Applications:
        1. Contour plots showing lines of constant error
        2. Heatmaps revealing optimal β regions
        3. Cross-sections showing error vs altitude for fixed β
        4. Optimization landscapes for β parameter tuning
        
        Grid Properties:
        - Rows represent altitudes (increasing upward)
        - Columns represent β values (increasing rightward)
        - Values represent percentage pressure errors
        - Positive values: exponential over-predicts pressure
        - Negative values: exponential under-predicts pressure
        
        Args:
            beta_range (tuple): (min_beta, max_beta) scale height range [m]
            altitude_range (tuple): (min_altitude, max_altitude) range [m]
            num_beta (int): Number of β grid points (default: 50)
            num_alt (int): Number of altitude grid points (default: 100)
            
        Returns:
            tuple: (beta_array, altitude_array, error_matrix)
                - beta_array: 1D array of β values [m]
                - altitude_array: 1D array of altitudes [m]  
                - error_matrix: 2D array of pressure errors [%]
                  Shape: (num_alt, num_beta)
                  
        Computational Complexity:
        O(num_alt × num_beta) = O(num_alt × num_beta) ISA calculations
        Default: 100 × 50 = 5,000 calculations
        
        Memory Usage:
        Error matrix: num_alt × num_beta × 8 bytes (float64)
        Default: 100 × 50 × 8 = 40 KB
        """
        # Generate linearly-spaced parameter arrays
        betas = np.linspace(beta_range[0], beta_range[1], num_beta)
        altitudes = np.linspace(altitude_range[0], altitude_range[1], num_alt)
        
        # Initialize error matrix: rows=altitudes, columns=betas
        pressure_errors = np.zeros((len(altitudes), len(betas)))
        
        # Populate error matrix through nested iteration
        for i, h in enumerate(altitudes):
            # Calculate ISA reference pressure at this altitude
            isa_results = ISACalculator.calculate_from_geometric(h)
            isa_pressure = isa_results['pressure']
            
            # Calculate errors for all β values at this altitude
            for j, beta in enumerate(betas):
                # Calculate exponential model pressure
                exp_pressure = ExponentialAtmosphere.calculate_pressure(h, beta)
                
                # Compute percentage error: (predicted - reference) / reference × 100%
                pressure_errors[i, j] = ((exp_pressure - isa_pressure) / isa_pressure * 100)
        
        return betas, altitudes, pressure_errors
