"""
Atmospheric Model Visualization and Data Processing

This module provides comprehensive visualization tools for atmospheric modeling
analysis. It implements advanced plotting techniques, mathematical interpolation,
and data processing algorithms to create publication-quality scientific
visualizations of atmospheric properties and model comparisons.

Visualization Capabilities:
1. 2D Error Heatmaps: Contour plots showing model accuracy across parameter space
2. Multi-Model Comparisons: Side-by-side analysis of ISA vs exponential models
3. Sensitivity Analysis: Parameter influence on model accuracy
4. Statistical Visualizations: Error distributions and performance metrics

Mathematical Framework:
The visualizer employs several mathematical techniques:
- Bilinear interpolation for smooth contour generation
- Logarithmic scaling for pressure/density data spanning orders of magnitude
- Color mapping algorithms for intuitive data representation
- Statistical analysis for error characterization

Data Processing Pipeline:
1. Sample Generation: Create high-resolution datasets for smooth plotting
2. Model Evaluation: Calculate atmospheric properties using multiple models
3. Error Analysis: Compute relative and absolute errors between models
4. Interpolation: Generate smooth surfaces from discrete data points
5. Rendering: Apply color maps, contours, and annotations for clarity

Color Scheme Design:
- Blue-White-Red (RdBu_r): Intuitive diverging colormap for errors
- Blue tones: ISA reference data (authoritative standard)
- Green tones: Optimized models (improved performance)
- Red tones: Standard models (baseline comparison)
- Yellow/Orange: Constants and reference lines

Plot Quality Standards:
- High DPI (150) for crisp publication-quality output
- Bold fonts and clear labels for readability
- Grid lines with transparency for visual guidance
- Legends positioned to avoid data obscuration
- Tight layout optimization for efficient space usage

File I/O Operations:
- PNG format for web compatibility and quality
- Descriptive filenames encoding plot parameters
- Automatic file closure for memory management
- Bbox_inches='tight' for optimal figure boundaries

Performance Considerations:
- Agg backend for headless server compatibility
- Memory-efficient array operations using NumPy
- Vectorized calculations for high-resolution datasets
- Figure closure after saving to prevent memory leaks
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server compatibility

try:
    from .isa_calculator import ISACalculator
    from .exponential_models import ExponentialAtmosphere
    from .optimizer import ScaleHeightOptimizer
except ImportError:
    from isa_calculator import ISACalculator
    from exponential_models import ExponentialAtmosphere
    from optimizer import ScaleHeightOptimizer

class AtmosphereVisualizer:
    """
    Advanced Visualization Engine for Atmospheric Models
    
    This class provides sophisticated plotting and data visualization capabilities
    for atmospheric modeling applications. It implements publication-quality
    scientific visualization techniques with emphasis on clarity, accuracy,
    and professional presentation standards.
    
    The visualizer supports multiple plot types, automatic color selection,
    mathematical interpolation, and comprehensive error analysis visualization.
    All plots are optimized for both digital display and print publication.
    """
    
    @staticmethod
    def plot_error_heatmap(h_min, h_max, beta_min=5000, beta_max=12000, optimal_beta=None):
        """
        Generate 2D error heatmap showing exponential model accuracy across parameter space.
        
        This function creates a comprehensive visualization of how exponential atmosphere
        model errors vary with both scale height (β) and altitude. The resulting contour
        plot reveals optimal parameter regions and quantifies model accuracy trade-offs.
        
        Mathematical Visualization:
        The heatmap displays the error surface E(h,β) where:
        E(h,β) = [P₀×exp(-h/β) - P_ISA(h)] / P_ISA(h) × 100%
        
        Visualization Techniques:
        1. Filled contours (contourf) for smooth color gradients
        2. Zero-error contour lines for optimal β identification
        3. Diverging colormap (RdBu_r) for intuitive error interpretation
        4. Overlay lines showing standard and optimal β values
        5. Altitude scaling to km for readability
        
        Color Interpretation:
        - Blue regions: Exponential model under-predicts pressure (negative error)
        - White regions: Minimal error between models
        - Red regions: Exponential model over-predicts pressure (positive error)
        - Black contour: Zero error line (perfect exponential match)
        
        Args:
            h_min (float): Minimum altitude for analysis [m]
            h_max (float): Maximum altitude for analysis [m]
            beta_min (float): Minimum scale height for parameter sweep [m]
            beta_max (float): Maximum scale height for parameter sweep [m]
            optimal_beta (float, optional): Optimal β to highlight [m]
            
        Returns:
            str: Filename of saved heatmap image
        """
        # Generate high-resolution error grid for smooth visualization
        betas, altitudes, errors = ExponentialAtmosphere.generate_error_grid(
            (beta_min, beta_max), (h_min, h_max), num_beta=100, num_alt=100
        )
        
        # Create figure with professional sizing for publication quality
        plt.figure(figsize=(12, 8))
        
        # Define error levels for contour generation (-50% to +50% range)
        # 21 levels provide smooth gradients without over-discretization
        levels = np.linspace(-50, 50, 21)
        
        # Generate filled contour plot with diverging colormap
        # RdBu_r (reversed Red-Blue) provides intuitive error interpretation
        contour = plt.contourf(betas, altitudes/1000, errors, levels=levels, cmap='RdBu_r')
        plt.colorbar(contour, label='Pressure Error (%)')
        
        # Add zero-error contour lines for optimal β identification
        # Black lines clearly show regions of minimal model error
        contour_lines = plt.contour(betas, altitudes/1000, errors, levels=[0], colors='black', linewidths=2)
        plt.clabel(contour_lines, inline=True, fontsize=10, fmt='0% error')
        
        # Highlight optimal β value if provided (from optimization results)
        if optimal_beta:
            plt.axvline(x=optimal_beta, color='lime', linewidth=3, linestyle='--', 
                       label=f'Optimal β = {optimal_beta:.0f} m')
        
        # Show standard β reference line for comparison
        plt.axvline(x=8000, color='yellow', linewidth=2, linestyle=':', 
                   label='Standard β = 8000 m')
        
        # Professional axis labeling with bold fonts for readability
        plt.xlabel('Scale Height β (meters)', fontsize=12, fontweight='bold')
        plt.ylabel('Altitude (km)', fontsize=12, fontweight='bold')
        plt.title(f'Exponential Model Error Landscape\nAltitude Range: {h_min/1000:.0f}-{h_max/1000:.0f} km', 
                 fontsize=14, fontweight='bold')
        plt.legend(loc='upper right', fontsize=11)
        plt.grid(True, alpha=0.3)  # Subtle grid for visual guidance
        
        # Optimize layout and save with high quality
        plt.tight_layout()
        filename = f'error_heatmap_{h_min}_{h_max}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()  # Free memory immediately
        
        return filename
    
    @staticmethod
    def plot_model_comparison(h_min, h_max, optimal_beta, num_points=200):
        """
        Generate comprehensive multi-panel comparison of atmospheric models.
        
        This function creates a sophisticated 2x2 subplot layout comparing ISA,
        optimized exponential, and standard exponential models across multiple
        atmospheric properties. The visualization enables detailed analysis of
        model accuracy, limitations, and performance trade-offs.
        
        Panel Layout:
        1. Top-left: Pressure profiles (log scale for wide dynamic range)
        2. Top-right: Pressure errors vs altitude (percentage deviations)
        3. Bottom-left: Temperature profiles (highlighting isothermal assumption)
        4. Bottom-right: Density profiles (log scale for exponential decay)
        
        Data Processing:
        - High-resolution sampling (200 points default) for smooth curves
        - Logarithmic scaling for pressure/density spanning orders of magnitude
        - Error calculations using percentage formulation for scale independence
        - Color coding consistent across all panels for model identification
        
        Args:
            h_min (float): Minimum altitude [m]
            h_max (float): Maximum altitude [m]  
            optimal_beta (float): Optimized scale height parameter [m]
            num_points (int): Resolution for curve generation (default: 200)
            
        Returns:
            str: Filename of saved comparison plot
        """
        altitudes = np.linspace(h_min, h_max, num_points)
        
        isa_pressures = []
        exp_optimal_pressures = []
        exp_standard_pressures = []
        isa_temperatures = []
        isa_densities = []
        exp_densities_optimal = []
        
        for h in altitudes:
            isa = ISACalculator.calculate_from_geometric(h)
            isa_pressures.append(isa['pressure'])
            isa_temperatures.append(isa['temperature_K'])
            isa_densities.append(isa['density'])
            
            exp_opt = ExponentialAtmosphere.calculate_all(h, optimal_beta)
            exp_optimal_pressures.append(exp_opt['pressure'])
            exp_densities_optimal.append(exp_opt['density'])
            
            exp_std = ExponentialAtmosphere.calculate_all(h, 8000)
            exp_standard_pressures.append(exp_std['pressure'])
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        ax1 = axes[0, 0]
        ax1.plot(altitudes/1000, isa_pressures, 'b-', linewidth=2.5, label='ISA (8-layer)')
        ax1.plot(altitudes/1000, exp_optimal_pressures, 'g--', linewidth=2, 
                label=f'Exponential (β={optimal_beta:.0f}m, optimized)')
        ax1.plot(altitudes/1000, exp_standard_pressures, 'r:', linewidth=2, 
                label='Exponential (β=8000m, standard)')
        ax1.set_xlabel('Altitude (km)', fontweight='bold')
        ax1.set_ylabel('Pressure (Pa)', fontweight='bold')
        ax1.set_title('Pressure Profile Comparison', fontsize=13, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
        
        ax2 = axes[0, 1]
        pressure_errors_optimal = [((exp - isa) / isa * 100) 
                                   for exp, isa in zip(exp_optimal_pressures, isa_pressures)]
        pressure_errors_standard = [((exp - isa) / isa * 100) 
                                    for exp, isa in zip(exp_standard_pressures, isa_pressures)]
        
        ax2.plot(altitudes/1000, pressure_errors_optimal, 'g-', linewidth=2, 
                label=f'Optimized (β={optimal_beta:.0f}m)')
        ax2.plot(altitudes/1000, pressure_errors_standard, 'r-', linewidth=2, 
                label='Standard (β=8000m)')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax2.fill_between(altitudes/1000, -5, 5, alpha=0.2, color='green', 
                        label='±5% tolerance')
        ax2.set_xlabel('Altitude (km)', fontweight='bold')
        ax2.set_ylabel('Pressure Error (%)', fontweight='bold')
        ax2.set_title('Pressure Error vs ISA', fontsize=13, fontweight='bold')
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        ax3 = axes[1, 0]
        ax3.plot(altitudes/1000, isa_temperatures, 'b-', linewidth=2.5, label='ISA (variable T)')
        ax3.axhline(y=288.15, color='orange', linestyle='--', linewidth=2, 
                   label='Exponential (constant T=288.15K)')
        ax3.set_xlabel('Altitude (km)', fontweight='bold')
        ax3.set_ylabel('Temperature (K)', fontweight='bold')
        ax3.set_title('Temperature Profile', fontsize=13, fontweight='bold')
        ax3.legend(loc='best')
        ax3.grid(True, alpha=0.3)
        
        ax4 = axes[1, 1]
        ax4.plot(altitudes/1000, isa_densities, 'b-', linewidth=2.5, label='ISA')
        ax4.plot(altitudes/1000, exp_densities_optimal, 'g--', linewidth=2, 
                label=f'Exponential (β={optimal_beta:.0f}m)')
        ax4.set_xlabel('Altitude (km)', fontweight='bold')
        ax4.set_ylabel('Density (kg/m³)', fontweight='bold')
        ax4.set_title('Density Profile Comparison', fontsize=13, fontweight='bold')
        ax4.legend(loc='upper right')
        ax4.grid(True, alpha=0.3)
        ax4.set_yscale('log')
        
        plt.suptitle(f'Atmospheric Model Comparison ({h_min/1000:.0f}-{h_max/1000:.0f} km)', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        plt.tight_layout()
        filename = f'model_comparison_{h_min}_{h_max}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    @staticmethod
    def plot_beta_sensitivity(h_test, beta_range=(5000, 12000), num_points=100):
        """Show how error changes with beta at a specific altitude"""
        betas = np.linspace(beta_range[0], beta_range[1], num_points)
        
        isa_results = ISACalculator.calculate_from_geometric(h_test)
        isa_pressure = isa_results['pressure']
        
        errors = []
        for beta in betas:
            exp_pressure = ExponentialAtmosphere.calculate_pressure(h_test, beta)
            error_pct = ((exp_pressure - isa_pressure) / isa_pressure * 100)
            errors.append(error_pct)
        
        plt.figure(figsize=(12, 7))
        plt.plot(betas, errors, 'b-', linewidth=2.5)
        plt.axhline(y=0, color='black', linestyle='-', linewidth=1)
        plt.axvline(x=8000, color='red', linestyle='--', linewidth=2, 
                   label='Standard β = 8000m')
        
        min_error_idx = np.argmin(np.abs(errors))
        optimal_beta_local = betas[min_error_idx]
        plt.axvline(x=optimal_beta_local, color='green', linestyle='--', linewidth=2,
                   label=f'Optimal β = {optimal_beta_local:.0f}m (for this altitude)')
        plt.scatter([optimal_beta_local], [errors[min_error_idx]], color='green', 
                   s=100, zorder=5)
        
        plt.fill_between(betas, -5, 5, alpha=0.2, color='green', label='±5% tolerance')
        
        plt.xlabel('Scale Height β (meters)', fontsize=12, fontweight='bold')
        plt.ylabel('Pressure Error (%)', fontsize=12, fontweight='bold')
        plt.title(f'How Scale Height Affects Error at {h_test/1000:.1f} km Altitude', 
                 fontsize=14, fontweight='bold')
        plt.legend(loc='best', fontsize=11)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        filename = f'beta_sensitivity_{h_test}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
