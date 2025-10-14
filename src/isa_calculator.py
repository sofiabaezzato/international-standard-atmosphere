import math

class ISACalculator:
    """International Standard Atmosphere Calculator"""
    
    R = 287.05287
    GAMMA = 1.4
    G0 = 9.80665
    RE = 6356766
    
    T0 = 288.15
    P0 = 101325
    RHO0 = 1.225
    
    LAYERS = [
        (0, 288.15, -0.0065),
        (11000, 216.65, 0.0),
        (20000, 216.65, 0.001),
        (32000, 228.65, 0.0028),
        (47000, 270.65, 0.0),
        (51000, 270.65, -0.0028),
        (71000, 214.65, -0.002),
        (86000, 186.946, 0.0)
    ]
    
    @staticmethod
    def geometric_to_geopotential(h_geom):
        return (ISACalculator.RE * h_geom) / (ISACalculator.RE + h_geom)
    
    @staticmethod
    def geopotential_to_geometric(h_geop):
        return (ISACalculator.RE * h_geop) / (ISACalculator.RE - h_geop)
    
    @staticmethod
    def get_layer(h_geop):
        for i in range(len(ISACalculator.LAYERS) - 1):
            if h_geop <= ISACalculator.LAYERS[i + 1][0]:
                return i
        return len(ISACalculator.LAYERS) - 1
    
    @staticmethod
    def calculate_isa(h_geop):
        layer_idx = ISACalculator.get_layer(h_geop)
        h_base, T_base, lapse_rate = ISACalculator.LAYERS[layer_idx]
        
        delta_h = h_geop - h_base
        T = T_base + lapse_rate * delta_h
        
        if abs(lapse_rate) < 1e-10:
            if layer_idx == 0:
                P_base = ISACalculator.P0
            else:
                P_base = ISACalculator.calculate_isa(h_base)[1]
            
            P = P_base * math.exp(-ISACalculator.G0 * delta_h / (ISACalculator.R * T_base))
        else:
            if layer_idx == 0:
                P_base = ISACalculator.P0
            else:
                P_base = ISACalculator.calculate_isa(h_base)[1]
            
            P = P_base * (T / T_base) ** (-ISACalculator.G0 / (lapse_rate * ISACalculator.R))
        
        rho = P / (ISACalculator.R * T)
        a = math.sqrt(ISACalculator.GAMMA * ISACalculator.R * T)
        
        return T, P, rho, a
    
    @staticmethod
    def calculate_from_geometric(h_geom):
        h_geop = ISACalculator.geometric_to_geopotential(h_geom)
        T, P, rho, a = ISACalculator.calculate_isa(h_geop)
        
        results = {
            'geometric_altitude': h_geom,
            'geopotential_altitude': h_geop,
            'temperature_K': T,
            'temperature_C': T - 273.15,
            'pressure': P,
            'density': rho,
            'speed_of_sound': a,
            'pressure_ratio': P / ISACalculator.P0,
            'density_ratio': rho / ISACalculator.RHO0
        }
        
        return results
    
    @staticmethod
    def calculate_error(h_geom):
        results_proper = ISACalculator.calculate_from_geometric(h_geom)
        T_approx, P_approx, rho_approx, a_approx = ISACalculator.calculate_isa(h_geom)
        
        errors = {
            'altitude_difference_m': h_geom - results_proper['geopotential_altitude'],
            'altitude_error_pct': ((h_geom - results_proper['geopotential_altitude']) / h_geom * 100) if h_geom > 0 else 0,
            'temperature_error_pct': ((T_approx - results_proper['temperature_K']) / results_proper['temperature_K'] * 100),
            'pressure_error_pct': ((P_approx - results_proper['pressure']) / results_proper['pressure'] * 100),
            'density_error_pct': ((rho_approx - results_proper['density']) / results_proper['density'] * 100),
            'speed_of_sound_error_pct': ((a_approx - results_proper['speed_of_sound']) / results_proper['speed_of_sound'] * 100)
        }
        
        return errors
