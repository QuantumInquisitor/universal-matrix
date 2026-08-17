#!/usr/bin/env python3
"""
Universal Playing Field: Dynamic Data Logger Module (v5.0 Spec)
Simulates or captures rolling environmental streams and logs matrix tracking
metrics directly into a structured, Excel-ready CSV spreadsheet log.
"""

import os
import sys
import time
from datetime import datetime

# Ensure local path can import the verified matrix core cleanly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import calculator as mc
except ImportError:
    print("CRITICAL ERROR: 'calculator.py' must be present in the same directory.")
    sys.exit(1)


def start_data_stream_logging(duration_seconds=10, sample_interval=1.0):
    """
    Captures a real-time tracking stream and dumps metrics to a local database spreadsheet.
    """
    output_filename = "matrix_history.csv"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
    
    # Establish clean spreadsheet data header columns
    headers = "Timestamp,Input_Psi,Boundary_Contribution,Total_Stabilized_Density\n"
    
    # Check if file exists, if not write header fields
    if not os.path.exists(output_path):
        with open(output_path, "w") as file:
            file.write(headers)
            
    print(f"Initializing matrix logging track -> File output target: {output_path}")
    print("Press Ctrl+C to terminate stream collection early.\n")
    
    start_time = time.time()
    try:
        while time.time() - start_time < duration_seconds:
            # Generate a dynamic simulation curve to simulate shifting atmospheric pressure inputs
            elapsed = time.time() - start_time
            simulated_psi = 13.5 + 5.0 * (elapsed % 10) # Safe fluctuating value envelope
            
            # Pipe the data straight through your verified logic formulas
            d_stab, ext_contrib = mc.calculate_axiom_6(simulated_psi)
            current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format raw data row values cleanly
            data_row = f"{current_time_str},{simulated_psi:.2f},{ext_contrib:.4f},{d_stab:.4f}\n"
            
            with open(output_path, "a") as file:
                file.write(data_row)
                
            print(f"[{current_time_str}] Logged State -> Psi: {simulated_psi:.2f} | Density: {d_stab:.4f}")
            time.sleep(sample_interval)
            
        print(f"\nSUCCESS: Data logging loop sequence concluded cleanly. File closed safely.")
    except KeyboardInterrupt:
        print(f"\nStream tracking intercepted manually. Data saved safely to: {output_path}")


if __name__ == "__main__":
    # Runs a quick 10-second data logging capture trial run
    start_data_stream_logging(duration_seconds=10, sample_interval=1.0)
