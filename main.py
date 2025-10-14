import os
from src import ISACalculator, ExponentialAtmosphere, ScaleHeightOptimizer, AtmosphereVisualizer

class EducationalInterface:
    """Interactive educational interface for atmospheric modeling"""
    
    @staticmethod
    def clear_screen():
        os.system('clear' if os.name != 'nt' else 'cls')
    
    @staticmethod
    def print_header(title):
        print("\n" + "="*80)
        print(f"  {title.upper()}")
        print("="*80 + "\n")
    
    @staticmethod
    def print_section(title):
        print(f"\n{'─'*80}")
        print(f"  {title}")
        print(f"{'─'*80}\n")
    
    @staticmethod
    def wait_for_user():
        input("\n  Press Enter to continue...")
    
    @staticmethod
    def tutorial_exponential_model():
        EducationalInterface.clear_screen()
        EducationalInterface.print_header("Understanding Exponential Atmosphere Models")
        
        print("  📚 CONCEPT: What is an Exponential Atmosphere Model?")
        print()
        print("  The exponential model is a SIMPLIFIED way to describe how air pressure and")
        print("  density decrease with altitude. It uses a single parameter called SCALE HEIGHT (β).")
        print()
        print("  The Formula:")
        print("    P(h) = P₀ × e^(-h/β)")
        print()
        print("  Where:")
        print("    • P(h) = Pressure at altitude h")
        print("    • P₀ = Sea level pressure (101,325 Pa)")
        print("    • h = Altitude (meters)")
        print("    • β = Scale height (meters) - THE KEY PARAMETER!")
        print()
        print("  💡 What is Scale Height (β)?")
        print()
        print("  Scale height tells you how 'quickly' the atmosphere thins out:")
        print()
        print("    • LARGER β (e.g., 10,000m) → Atmosphere thins out SLOWLY")
        print("      → Pressure stays higher at altitude")
        print()
        print("    • SMALLER β (e.g., 6,000m) → Atmosphere thins out QUICKLY")
        print("      → Pressure drops faster with altitude")
        print()
        print("  The standard value is β = 8,000 meters, which means:")
        print("    → At 8,000m altitude, pressure drops to 37% of sea level (1/e)")
        print("    → At 16,000m altitude, pressure drops to 14% of sea level (1/e²)")
        print()
        EducationalInterface.wait_for_user()
        
        EducationalInterface.clear_screen()
        EducationalInterface.print_section("Why Do We Need to Optimize β?")
        
        print("  🎯 THE PROBLEM:")
        print()
        print("  The exponential model assumes the atmosphere is ISOTHERMAL (constant")
        print("  temperature), but in reality, temperature CHANGES with altitude:")
        print()
        print("    • 0-11 km (Troposphere): Temperature DECREASES at -6.5°C per km")
        print("    • 11-20 km (Tropopause): Temperature CONSTANT at -56.5°C")
        print("    • 20-47 km (Stratosphere): Temperature INCREASES (ozone heating)")
        print()
        print("  Because the real atmosphere has these layers, NO SINGLE β value will")
        print("  perfectly match the ISA model at all altitudes!")
        print()
        print("  🔧 THE SOLUTION:")
        print()
        print("  We can OPTIMIZE β to find the best fit for a specific altitude range:")
        print()
        print("    • For low altitudes (0-10 km): β ≈ 7,400m works best")
        print("    • For mid altitudes (0-30 km): β ≈ 8,500m works best")
        print("    • For high altitudes (0-50 km): β ≈ 9,200m works best")
        print()
        print("  This is what our optimizer does - it finds the β that minimizes the")
        print("  difference between the simple exponential model and the complex ISA model!")
        print()
        EducationalInterface.wait_for_user()
    
    @staticmethod
    def tutorial_optimization():
        EducationalInterface.clear_screen()
        EducationalInterface.print_header("Understanding the Optimization Process")
        
        print("  🔬 OPTIMIZATION: Finding the Best Scale Height (β)")
        print()
        print("  The goal is to find the β value that makes our exponential model as")
        print("  close as possible to the accurate ISA model.")
        print()
        print("  📊 The Method: Least Squares Optimization")
        print()
        print("  1. Choose an altitude range (e.g., 0 to 20,000 meters)")
        print()
        print("  2. Calculate ISA pressures at many points in this range")
        print()
        print("  3. Try different β values and calculate exponential model pressures")
        print()
        print("  4. Find the β that MINIMIZES the sum of squared errors:")
        print()
        print("       Error = Σ (P_exponential - P_ISA)²")
        print()
        print("  5. This optimal β gives the best fit for your chosen altitude range!")
        print()
        print("  🎨 Visualizing the Error Landscape")
        print()
        print("  The 2D heatmap shows:")
        print()
        print("    • X-axis: Different β values (5,000 to 12,000 meters)")
        print("    • Y-axis: Different altitudes")
        print("    • Color: Percentage error (Red = overestimate, Blue = underestimate)")
        print()
        print("  The BLACK LINE shows where error = 0%")
        print("  The GREEN LINE shows the optimal β (best average fit)")
        print()
        print("  💡 Key Insight:")
        print()
        print("  You'll notice that NO single β value gives 0% error at ALL altitudes!")
        print("  This shows why the multi-layer ISA model is more accurate than a simple")
        print("  exponential model - but the exponential model is much easier to calculate!")
        print()
        EducationalInterface.wait_for_user()
    
    @staticmethod
    def explore_altitude_range():
        EducationalInterface.clear_screen()
        EducationalInterface.print_header("Optimize β for Your Altitude Range")
        
        print("  Let's find the optimal scale height for your specific altitude range!")
        print()
        
        try:
            h_min = float(input("  Enter minimum altitude (meters, e.g., 0): ").strip())
            h_max = float(input("  Enter maximum altitude (meters, e.g., 20000): ").strip())
            
            if h_min < 0 or h_max < 0:
                print("\n  ❌ Error: Altitudes must be non-negative!")
                EducationalInterface.wait_for_user()
                return
            
            if h_min >= h_max:
                print("\n  ❌ Error: Minimum altitude must be less than maximum!")
                EducationalInterface.wait_for_user()
                return
            
            if h_max > 86000:
                print(f"\n  ⚠️  Warning: Maximum altitude {h_max/1000:.1f} km exceeds ISA model range (86 km)")
                print("  Results may be less accurate.")
                EducationalInterface.wait_for_user()
            
            print(f"\n  🔄 Optimizing for altitude range: {h_min/1000:.1f} km to {h_max/1000:.1f} km...")
            print("  This may take a moment...\n")
            
            analysis = ScaleHeightOptimizer.analyze_optimization(h_min, h_max)
            opt_results = analysis['optimization']
            optimal_beta = opt_results['optimal_beta']
            
            EducationalInterface.print_section("Optimization Results")
            
            print(f"  ✅ OPTIMAL SCALE HEIGHT: β = {optimal_beta:.0f} meters")
            print(f"  📊 Root Mean Square Error: {opt_results['rmse']:.2f} Pa ({opt_results['rmse_percentage']:.2f}%)")
            print(f"  📏 Altitude Range: {h_min/1000:.1f} - {h_max/1000:.1f} km")
            print()
            
            EducationalInterface.print_section("Model Comparison at Key Altitudes")
            print(f"  {'Altitude':<12} {'ISA Pressure':<18} {'Optimal β Error':<18} {'Standard β=8000m Error':<25}")
            print(f"  {'(km)':<12} {'(Pa)':<18} {'(%)':<18} {'(%)':<25}")
            print(f"  {'-'*80}")
            
            for comp in analysis['comparisons']:
                h_km = comp['altitude'] / 1000
                isa_p = comp['isa_pressure']
                opt_err = comp['optimal_error_pct']
                std_err = comp['standard_error_pct']
                
                print(f"  {h_km:<12.1f} {isa_p:<18.2f} {opt_err:>+16.2f}% {std_err:>+23.2f}%")
            
            print()
            EducationalInterface.print_section("Educational Insights")
            
            if h_max <= 15000:
                print(f"  📚 For low altitudes (0-15 km), optimal β ≈ {optimal_beta:.0f}m is LOWER than")
                print("     the standard 8,000m because the troposphere has a temperature gradient")
                print("     that causes faster pressure decrease.")
            elif h_max <= 30000:
                print(f"  📚 For mid altitudes (0-30 km), optimal β ≈ {optimal_beta:.0f}m is close to")
                print("     the standard 8,000m, balancing tropospheric cooling with stratospheric")
                print("     isothermal regions.")
            else:
                print(f"  📚 For high altitudes (0-{h_max/1000:.0f} km), optimal β ≈ {optimal_beta:.0f}m is HIGHER than")
                print("     the standard 8,000m because stratospheric warming affects the average")
                print("     temperature profile.")
            
            print()
            diff_from_standard = optimal_beta - 8000
            if abs(diff_from_standard) < 500:
                print(f"  💡 Your optimal β is very close to the standard value (difference: {diff_from_standard:+.0f}m).")
                print("     This means β = 8,000m is a good approximation for your altitude range!")
            elif diff_from_standard > 0:
                print(f"  💡 Your optimal β is {diff_from_standard:.0f}m HIGHER than standard.")
                print("     Using β = 8,000m would UNDERESTIMATE pressures in your range.")
            else:
                print(f"  💡 Your optimal β is {abs(diff_from_standard):.0f}m LOWER than standard.")
                print("     Using β = 8,000m would OVERESTIMATE pressures in your range.")
            
            print()
            generate_viz = input("  Would you like to generate visualizations? (y/n): ").strip().lower()
            
            if generate_viz == 'y':
                print("\n  📊 Generating visualizations...")
                
                heatmap_file = AtmosphereVisualizer.plot_error_heatmap(h_min, h_max, optimal_beta=optimal_beta)
                print(f"  ✅ Error heatmap saved: {heatmap_file}")
                
                comparison_file = AtmosphereVisualizer.plot_model_comparison(h_min, h_max, optimal_beta)
                print(f"  ✅ Model comparison saved: {comparison_file}")
                
                print("\n  🎨 Visualizations created! Check the files above to see:")
                print("     • How error changes with β and altitude (heatmap)")
                print("     • Side-by-side comparison of ISA vs exponential models")
            
            EducationalInterface.wait_for_user()
            
        except ValueError:
            print("\n  ❌ Error: Please enter valid numbers!")
            EducationalInterface.wait_for_user()
        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            EducationalInterface.wait_for_user()
    
    @staticmethod
    def explore_single_altitude():
        EducationalInterface.clear_screen()
        EducationalInterface.print_header("Explore β Sensitivity at Single Altitude")
        
        print("  Let's see how the scale height β affects error at a specific altitude!")
        print()
        
        try:
            h_test = float(input("  Enter altitude to test (meters, e.g., 10000): ").strip())
            
            if h_test < 0:
                print("\n  ❌ Error: Altitude must be non-negative!")
                EducationalInterface.wait_for_user()
                return
            
            print(f"\n  🔍 Analyzing β sensitivity at {h_test/1000:.1f} km altitude...")
            
            isa_results = ISACalculator.calculate_from_geometric(h_test)
            
            EducationalInterface.print_section(f"ISA Conditions at {h_test/1000:.1f} km")
            print(f"  Temperature: {isa_results['temperature_K']:.2f} K ({isa_results['temperature_C']:.2f}°C)")
            print(f"  Pressure:    {isa_results['pressure']:.2f} Pa")
            print(f"  Density:     {isa_results['density']:.4f} kg/m³")
            
            EducationalInterface.print_section("Testing Different Scale Heights")
            
            test_betas = [6000, 7000, 8000, 9000, 10000]
            print(f"  {'β (meters)':<15} {'Exp Pressure (Pa)':<20} {'Error (%)':<15}")
            print(f"  {'-'*50}")
            
            for beta in test_betas:
                exp_pressure = ExponentialAtmosphere.calculate_pressure(h_test, beta)
                error = ((exp_pressure - isa_results['pressure']) / isa_results['pressure'] * 100)
                marker = " ← Standard" if beta == 8000 else ""
                print(f"  {beta:<15} {exp_pressure:<20.2f} {error:>+13.2f}%{marker}")
            
            print()
            generate_viz = input("  Generate β sensitivity plot? (y/n): ").strip().lower()
            
            if generate_viz == 'y':
                print(f"\n  📊 Generating sensitivity plot for {h_test/1000:.1f} km altitude...")
                sensitivity_file = AtmosphereVisualizer.plot_beta_sensitivity(h_test)
                print(f"  ✅ Sensitivity plot saved: {sensitivity_file}")
                print("\n  🎨 The plot shows how error changes across β values from 5,000 to 12,000m")
                print("     • Green line = optimal β for this specific altitude")
                print("     • Red line = standard β = 8,000m")
            
            EducationalInterface.wait_for_user()
            
        except ValueError:
            print("\n  ❌ Error: Please enter a valid number!")
            EducationalInterface.wait_for_user()
        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            EducationalInterface.wait_for_user()
    
    @staticmethod
    def quick_comparison():
        EducationalInterface.clear_screen()
        EducationalInterface.print_header("Quick ISA Calculator")
        
        print("  Calculate atmospheric conditions at any altitude using the ISA model")
        print()
        
        try:
            altitude = float(input("  Enter altitude (meters): ").strip())
            
            if altitude < 0:
                print("\n  ❌ Error: Altitude must be non-negative!")
                EducationalInterface.wait_for_user()
                return
            
            results = ISACalculator.calculate_from_geometric(altitude)
            errors = ISACalculator.calculate_error(altitude)
            
            EducationalInterface.print_section(f"ISA Results at {altitude/1000:.2f} km")
            
            print(f"  Geometric Altitude:     {results['geometric_altitude']:>12.2f} m")
            print(f"  Geopotential Altitude:  {results['geopotential_altitude']:>12.2f} m")
            print(f"  Difference:             {errors['altitude_difference_m']:>12.2f} m")
            print()
            print(f"  Temperature:            {results['temperature_K']:>12.2f} K ({results['temperature_C']:>7.2f}°C)")
            print(f"  Pressure:               {results['pressure']:>12.2f} Pa")
            print(f"  Density:                {results['density']:>12.4f} kg/m³")
            print(f"  Speed of Sound:         {results['speed_of_sound']:>12.2f} m/s")
            print()
            print(f"  Pressure Ratio:         {results['pressure_ratio']:>12.6f}")
            print(f"  Density Ratio:          {results['density_ratio']:>12.6f}")
            
            exp_standard = ExponentialAtmosphere.calculate_all(altitude, 8000)
            exp_error = ((exp_standard['pressure'] - results['pressure']) / results['pressure'] * 100)
            
            EducationalInterface.print_section("Exponential Model Comparison (β=8000m)")
            print(f"  Exponential Pressure:   {exp_standard['pressure']:>12.2f} Pa")
            print(f"  Error vs ISA:           {exp_error:>+12.2f} %")
            print()
            
            if abs(exp_error) < 5:
                print("  ✅ The simple exponential model (β=8000m) is quite accurate at this altitude!")
            elif abs(exp_error) < 15:
                print("  ⚠️  The exponential model has moderate error at this altitude.")
                print("     Consider using the ISA model for precise calculations.")
            else:
                print("  ❌ The exponential model has significant error at this altitude!")
                print("     You should use the ISA model or optimize β for this range.")
            
            EducationalInterface.wait_for_user()
            
        except ValueError:
            print("\n  ❌ Error: Please enter a valid number!")
            EducationalInterface.wait_for_user()
        except Exception as e:
            print(f"\n  ❌ Error: {e}")
            EducationalInterface.wait_for_user()
    
    @staticmethod
    def main_menu():
        while True:
            EducationalInterface.clear_screen()
            EducationalInterface.print_header("Interactive Atmosphere Model Learning Tool")
            
            print("  Welcome! This tool helps you understand atmospheric models and optimization.")
            print()
            print("  📚 LEARN THE CONCEPTS:")
            print("     1. What is an Exponential Atmosphere Model?")
            print("     2. How Does Optimization Work?")
            print()
            print("  🔬 EXPLORE & EXPERIMENT:")
            print("     3. Optimize β for an Altitude Range")
            print("     4. Explore β Sensitivity at Single Altitude")
            print("     5. Quick ISA Calculator")
            print()
            print("  ❌ EXIT:")
            print("     6. Quit")
            print()
            
            choice = input("  Enter your choice (1-6): ").strip()
            
            if choice == '1':
                EducationalInterface.tutorial_exponential_model()
            elif choice == '2':
                EducationalInterface.tutorial_optimization()
            elif choice == '3':
                EducationalInterface.explore_altitude_range()
            elif choice == '4':
                EducationalInterface.explore_single_altitude()
            elif choice == '5':
                EducationalInterface.quick_comparison()
            elif choice == '6':
                EducationalInterface.clear_screen()
                print("\n  Thank you for using the Atmosphere Model Learning Tool!")
                print("  Keep exploring atmospheric physics! 🚀\n")
                break
            else:
                print("\n  ❌ Invalid choice. Please enter a number between 1 and 6.")
                EducationalInterface.wait_for_user()

if __name__ == "__main__":
    EducationalInterface.main_menu()
