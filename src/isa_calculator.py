"""
International Standard Atmosphere (ISA) Calculator

This module implements the International Standard Atmosphere model according to 
ISO 2533:1975 standard. The ISA provides a reference atmospheric model for 
engineering and scientific calculations, defining how atmospheric properties 
(temperature, pressure, density) vary with altitude under standard conditions.

Physical Basis:
The atmosphere is modeled as 8 distinct layers, each with specific temperature 
lapse rates (dT/dh). The model assumes:
- Hydrostatic equilibrium: dP = -ρg dh
- Ideal gas law: P = ρRT
- Constant gravitational acceleration (corrected for geopotential height)
- Standard atmospheric composition (dry air)

Mathematical Foundation:
For layers with non-zero lapse rate: P = P_base × (T/T_base)^(-g₀M/RL)
For isothermal layers: P = P_base × exp(-g₀M×Δh/RT)
Where: g₀ = standard gravity, M = molar mass, R = gas constant, L = lapse rate

References:
- ISO 2533:1975 Standard Atmosphere
- ICAO Standard Atmosphere (Doc 7488/3)
- U.S. Standard Atmosphere, 1976
"""

import math

class ISACalculator:
    """
    International Standard Atmosphere Calculator
    
    Implements the 8-layer atmospheric model covering altitudes from sea level 
    to 86 km. Each layer is characterized by its base altitude, base temperature,
    and temperature lapse rate.
    """
    
    # Physical Constants (ISO 2533:1975 standard values)
    R = 287.05287          # Specific gas constant for dry air [J/(kg·K)]
    GAMMA = 1.4            # Ratio of specific heats for dry air (cp/cv) [-]
    G0 = 9.80665          # Standard gravitational acceleration [m/s²]
    RE = 6356766          # Earth radius for geopotential calculations [m]
    
    # Sea Level Standard Conditions (ISA reference state)
    T0 = 288.15           # Standard temperature at sea level [K]
    P0 = 101325           # Standard pressure at sea level [Pa]
    RHO0 = 1.225          # Standard density at sea level [kg/m³]
    
    # Atmospheric Layer Definitions
    # Each tuple contains: (base_altitude [m], base_temperature [K], lapse_rate [K/m])
    # Lapse rate convention: negative = temperature decreases with altitude
    LAYERS = [
        (0, 288.15, -0.0065),      # Troposphere: sea level to 11 km
        (11000, 216.65, 0.0),      # Tropopause: 11 km to 20 km (isothermal)
        (20000, 216.65, 0.001),    # Lower Stratosphere: 20 km to 32 km
        (32000, 228.65, 0.0028),   # Upper Stratosphere: 32 km to 47 km
        (47000, 270.65, 0.0),      # Stratopause: 47 km to 51 km (isothermal)
        (51000, 270.65, -0.0028),  # Lower Mesosphere: 51 km to 71 km
        (71000, 214.65, -0.002),   # Upper Mesosphere: 71 km to 86 km
        (86000, 186.946, 0.0)      # Mesopause: 86 km and above (isothermal)
    ]
    
    @staticmethod
    def geometric_to_geopotential(h_geom):
        """
        Convert geometric altitude to geopotential altitude.
        
        Geopotential altitude accounts for the variation of gravitational acceleration
        with altitude. It simplifies atmospheric calculations by allowing the use of
        constant gravitational acceleration g₀ in hydrostatic equations.
        
        Mathematical Formula:
        h_geopotential = (R_E × h_geometric) / (R_E + h_geometric)
        
        Where:
        - R_E = Earth radius = 6,356,766 m (mean radius for atmosphere calculations)
        - h_geometric = actual altitude above sea level [m]
        
        Physical Interpretation:
        At high altitudes, gravitational acceleration decreases as g = g₀(R_E/(R_E+h))².
        Geopotential altitude compensates for this effect, allowing simplified equations.
        
        Args:
            h_geom (float): Geometric altitude above sea level [m]
            
        Returns:
            float: Geopotential altitude [m]
            
        Example:
            At 20 km geometric altitude:
            h_geop = (6,356,766 × 20,000) / (6,356,766 + 20,000) = 19,937 m
            Difference: 63 m (0.3% error if ignored)
        """
        return (ISACalculator.RE * h_geom) / (ISACalculator.RE + h_geom)
    
    @staticmethod
    def geopotential_to_geometric(h_geop):
        """
        Convert geopotential altitude back to geometric altitude.
        
        This is the inverse transformation of geometric_to_geopotential().
        Used when atmospheric calculations require actual geometric altitude
        (e.g., GPS altitude, aircraft navigation).
        
        Mathematical Formula:
        h_geometric = (R_E × h_geopotential) / (R_E - h_geopotential)
        
        Args:
            h_geop (float): Geopotential altitude [m]
            
        Returns:
            float: Geometric altitude above sea level [m]
            
        Note:
            This function has a singularity at h_geop = R_E, which corresponds
            to infinite geometric altitude. In practice, this is never reached
            within the atmospheric domain (0-86 km).
        """
        return (ISACalculator.RE * h_geop) / (ISACalculator.RE - h_geop)
    
    @staticmethod
    def get_layer(h_geop):
        """
        Determine which atmospheric layer contains the given geopotential altitude.
        
        The ISA model divides the atmosphere into 8 distinct layers, each with
        specific temperature lapse rates. This function performs a sequential
        search to find the appropriate layer index.
        
        Search Algorithm:
        1. Compare altitude with each layer's upper boundary
        2. Return the first layer where h_geop ≤ next_layer_base_altitude
        3. If altitude exceeds all boundaries, return the highest layer index
        
        Args:
            h_geop (float): Geopotential altitude [m]
            
        Returns:
            int: Layer index (0-7) corresponding to ISACalculator.LAYERS
            
        Layer Boundaries:
        Layer 0: 0 - 11,000 m      (Troposphere)
        Layer 1: 11,000 - 20,000 m (Tropopause)
        Layer 2: 20,000 - 32,000 m (Lower Stratosphere)
        Layer 3: 32,000 - 47,000 m (Upper Stratosphere)
        Layer 4: 47,000 - 51,000 m (Stratopause)
        Layer 5: 51,000 - 71,000 m (Lower Mesosphere)
        Layer 6: 71,000 - 86,000 m (Upper Mesosphere)
        Layer 7: 86,000+ m          (Mesopause and above)
        
        Computational Complexity: O(n) where n = number of layers (8)
        """
        for i in range(len(ISACalculator.LAYERS) - 1):
            if h_geop <= ISACalculator.LAYERS[i + 1][0]:
                return i
        return len(ISACalculator.LAYERS) - 1
    
    @staticmethod
    def calculate_isa(h_geop):
        """
        Calculate atmospheric properties at a given geopotential altitude using ISA model.
        
        This is the core function that implements the International Standard Atmosphere
        calculations. It handles both isothermal and non-isothermal atmospheric layers
        using the appropriate mathematical formulations derived from hydrostatic equilibrium
        and the ideal gas law.
        
        Theoretical Foundation:
        Starting from hydrostatic equilibrium: dP = -ρg dh
        Combined with ideal gas law: ρ = P/(RT)
        Yields: dP/P = -g/(RT) dh
        
        For non-isothermal layers (L ≠ 0):
        Integration with T = T_base + L(h - h_base) gives:
        P = P_base × (T/T_base)^(-g₀/(L×R))
        
        For isothermal layers (L = 0):
        Integration with T = constant gives:
        P = P_base × exp(-g₀×Δh/(R×T))
        
        Args:
            h_geop (float): Geopotential altitude [m]
            
        Returns:
            tuple: (temperature [K], pressure [Pa], density [kg/m³], speed_of_sound [m/s])
            
        Algorithm Steps:
        1. Determine atmospheric layer containing the altitude
        2. Extract layer parameters (base altitude, temperature, lapse rate)
        3. Calculate temperature using linear lapse rate
        4. Determine base pressure (sea level or from previous layer)
        5. Apply appropriate pressure formula (isothermal vs non-isothermal)
        6. Calculate density using ideal gas law
        7. Calculate speed of sound using thermodynamic relations
        """
        # Step 1: Determine which atmospheric layer contains this altitude
        layer_idx = ISACalculator.get_layer(h_geop)
        h_base, T_base, lapse_rate = ISACalculator.LAYERS[layer_idx]
        
        # Step 2: Calculate altitude difference within the layer
        delta_h = h_geop - h_base
        
        # Step 3: Calculate temperature using linear lapse rate
        # T = T_base + L × Δh (where L is lapse rate in K/m)
        T = T_base + lapse_rate * delta_h
        
        # Step 4: Determine base pressure for this layer
        # For sea level layer (index 0), use standard pressure P₀
        # For higher layers, recursively calculate pressure at layer base
        if layer_idx == 0:
            P_base = ISACalculator.P0
        else:
            P_base = ISACalculator.calculate_isa(h_base)[1]
        
        # Step 5: Calculate pressure using appropriate formula
        # Check if layer is isothermal (lapse rate ≈ 0)
        if abs(lapse_rate) < 1e-10:
            # Isothermal Layer Formula:
            # P = P_base × exp(-g₀ × Δh / (R × T))
            # This comes from integrating dP/P = -g/(RT) dh with constant T
            P = P_base * math.exp(-ISACalculator.G0 * delta_h / (ISACalculator.R * T_base))
        else:
            # Non-Isothermal Layer Formula:
            # P = P_base × (T/T_base)^(-g₀/(L×R))
            # This comes from integrating dP/P = -g/(RT) dh with T = T_base + L×Δh
            # The exponent -g₀/(L×R) is dimensionless and represents the barometric formula
            P = P_base * (T / T_base) ** (-ISACalculator.G0 / (lapse_rate * ISACalculator.R))
        
        # Step 6: Calculate density using ideal gas law
        # ρ = P/(R×T) where R is specific gas constant for dry air
        rho = P / (ISACalculator.R * T)
        
        # Step 7: Calculate speed of sound using thermodynamic relation
        # a = √(γ×R×T) where γ is ratio of specific heats (cp/cv = 1.4 for air)
        # This comes from acoustic theory: a² = (∂P/∂ρ)_s for isentropic processes
        a = math.sqrt(ISACalculator.GAMMA * ISACalculator.R * T)
        
        return T, P, rho, a
    
    @staticmethod
    def calculate_from_geometric(h_geom):
        """
        Calculate ISA atmospheric properties for a given geometric altitude.
        
        This is the main user interface function that handles the complete
        calculation process including altitude conversion and results formatting.
        Most applications should use this function rather than calculate_isa()
        directly, as it properly handles geometric-to-geopotential conversion.
        
        Process Flow:
        1. Convert geometric altitude to geopotential altitude
        2. Perform ISA calculations using geopotential altitude
        3. Format results into a comprehensive dictionary
        4. Include both absolute values and standard ratios
        
        Args:
            h_geom (float): Geometric altitude above sea level [m]
            
        Returns:
            dict: Comprehensive atmospheric properties containing:
                - geometric_altitude [m]: Input altitude
                - geopotential_altitude [m]: Corrected altitude for calculations
                - temperature_K [K]: Absolute temperature
                - temperature_C [°C]: Celsius temperature
                - pressure [Pa]: Absolute pressure
                - density [kg/m³]: Air density
                - speed_of_sound [m/s]: Acoustic velocity
                - pressure_ratio [-]: P/P₀ (dimensionless pressure ratio)
                - density_ratio [-]: ρ/ρ₀ (dimensionless density ratio)
                
        Standard Ratios:
        Pressure and density ratios are commonly used in aerospace engineering
        for performance calculations and are dimensionless quantities that
        facilitate comparison across different altitudes.
        """
        # Step 1: Convert geometric to geopotential altitude
        # This correction becomes significant above ~10 km altitude
        h_geop = ISACalculator.geometric_to_geopotential(h_geom)
        
        # Step 2: Perform ISA calculations using corrected altitude
        T, P, rho, a = ISACalculator.calculate_isa(h_geop)
        
        # Step 3: Format results into comprehensive output dictionary
        results = {
            'geometric_altitude': h_geom,                    # Original input altitude [m]
            'geopotential_altitude': h_geop,                # Corrected altitude [m]
            'temperature_K': T,                             # Absolute temperature [K]
            'temperature_C': T - 273.15,                    # Celsius temperature [°C]
            'pressure': P,                                  # Absolute pressure [Pa]
            'density': rho,                                 # Air density [kg/m³]
            'speed_of_sound': a,                           # Acoustic velocity [m/s]
            'pressure_ratio': P / ISACalculator.P0,        # Dimensionless P/P₀ [-]
            'density_ratio': rho / ISACalculator.RHO0      # Dimensionless ρ/ρ₀ [-]
        }
        
        return results
    
    @staticmethod
    def calculate_error(h_geom):
        """
        Calculate errors introduced by approximating geometric altitude as geopotential.
        
        This function quantifies the accuracy impact of ignoring the geometric-to-
        geopotential altitude conversion. At low altitudes, the error is negligible,
        but it becomes significant at higher altitudes where gravitational correction
        is important.
        
        Error Analysis Method:
        1. Calculate "proper" results using geometric→geopotential conversion
        2. Calculate "approximate" results using geometric altitude directly
        3. Compute percentage errors for all atmospheric properties
        
        The altitude error represents the difference between geometric and geopotential
        altitudes, while property errors show how this altitude difference propagates
        through the atmospheric calculations.
        
        Args:
            h_geom (float): Geometric altitude above sea level [m]
            
        Returns:
            dict: Error analysis containing:
                - altitude_difference_m [m]: h_geom - h_geop
                - altitude_error_pct [%]: Relative altitude error
                - temperature_error_pct [%]: Temperature calculation error
                - pressure_error_pct [%]: Pressure calculation error  
                - density_error_pct [%]: Density calculation error
                - speed_of_sound_error_pct [%]: Acoustic velocity error
                
        Typical Error Magnitudes:
        - At 10 km: altitude error ~0.2%, property errors ~0.1%
        - At 20 km: altitude error ~0.3%, property errors ~0.5%
        - At 50 km: altitude error ~0.8%, property errors ~2-3%
        """
        # Calculate proper results using geometric→geopotential conversion
        results_proper = ISACalculator.calculate_from_geometric(h_geom)
        
        # Calculate approximate results using geometric altitude directly
        # This simulates the error introduced by ignoring altitude correction
        T_approx, P_approx, rho_approx, a_approx = ISACalculator.calculate_isa(h_geom)
        
        # Compute percentage errors for all properties
        # Error formula: (approximate - proper) / proper × 100%
        errors = {
            'altitude_difference_m': h_geom - results_proper['geopotential_altitude'],
            'altitude_error_pct': ((h_geom - results_proper['geopotential_altitude']) / h_geom * 100) if h_geom > 0 else 0,
            'temperature_error_pct': ((T_approx - results_proper['temperature_K']) / results_proper['temperature_K'] * 100),
            'pressure_error_pct': ((P_approx - results_proper['pressure']) / results_proper['pressure'] * 100),
            'density_error_pct': ((rho_approx - results_proper['density']) / results_proper['density'] * 100),
            'speed_of_sound_error_pct': ((a_approx - results_proper['speed_of_sound']) / results_proper['speed_of_sound'] * 100)
        }
        
        return errors
