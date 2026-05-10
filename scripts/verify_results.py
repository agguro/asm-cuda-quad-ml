#!/usr/bin/env python3
import sys
import cmath
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: verify_results.py <input.csv>")
        sys.exit(1)

    csv_path = sys.argv[1]
    
    # Get file size for a rough progress estimate
    file_size = os.path.getsize(csv_path)
    bytes_processed = 0
    
    # Use binary mode for stdout to ensure clean newline handling
    stdout = sys.stdout.buffer

    # Write a small header to stderr so it doesn't pollute the CSV output
    sys.stderr.write(f"--- High-Precision Verification ---\n")

    with open(csv_path, 'r', newline='') as f:
        for i, line in enumerate(f, 1):
            bytes_processed += len(line)
            
            clean_line = line.strip('\r\n')
            if not clean_line: 
                continue
            
            # 1. Parse exactly what the GPU solver sees
            try:
                parts = [float(x) for x in clean_line.split(',')]
                a = complex(parts[0], parts[1])
                b = complex(parts[2], parts[3])
                c = complex(parts[4], parts[5])
                
                # 2. Math (Double Precision)
                d = b**2 - 4*a*c
                sqrt_d = cmath.sqrt(d)
                r1 = (-b + sqrt_d) / (2*a)
                r2 = (-b - sqrt_d) / (2*a)
                
                # 3. Formatting (Using .6f for f64 alignment)
                # Reconstruct: a_r, a_i, b_r, b_i, c_r, c_i, r1_r, r1_i, r2_r, r2_i
                res = (f"{parts[0]:.6f},{parts[1]:.6f},{parts[2]:.6f},{parts[3]:.6f},"
                       f"{parts[4]:.6f},{parts[5]:.6f},{r1.real:.6f},{r1.imag:.6f},"
                       f"{r2.real:.6f},{r2.imag:.6f}\n")
                
                stdout.write(res.encode('ascii'))

            except (ValueError, IndexError):
                continue

            # 4. Progress Feedback to stderr (so it doesn't go into the results file)
            if i % 10000 == 0:
                progress = (bytes_processed / file_size) * 100
                sys.stderr.write(f"\r  > Verifying: {i:,} rows ({progress:.1f}%) ")
                sys.stderr.flush()

    sys.stderr.write(f"\r  > Verifying: Complete! {i:,} rows processed.    \n")

if __name__ == "__main__":
    main()