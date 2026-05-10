#!/usr/bin/env python3

import csv
import random
import cmath
import sys
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Generate random complex quadratic equations.")
    parser.add_argument("count", type=int, nargs='?', default=50, help="Number of equations to generate")
    parser.add_argument("--output", type=str, help="Full path for the inputs.csv file")
    args = parser.parse_args()

    # Determine paths based on --output argument
    if args.output:
        inputs_path = args.output
        base_dir = os.path.dirname(inputs_path)
        solved_path = os.path.join(base_dir, "expected_solved.csv")
    else:
        inputs_path = "inputs.csv"
        solved_path = "expected_solved.csv"

    print(f"--- High-Precision Data Generation ---")
    print(f"Target: {args.count:,} equations")
    
    try:
        with open(inputs_path, 'w', newline='') as f_in, \
             open(solved_path, 'w', newline='') as f_sol:
            
            writer_in = csv.writer(f_in)
            writer_sol = csv.writer(f_sol)

            for i in range(1, args.count + 1):
                # 1. Generate Coefficients
                a_r, a_i = random.uniform(-10.0, 10.0), random.uniform(-10.0, 10.0)
                while abs(complex(a_r, a_i)) < 0.1: # Avoid division by zero
                    a_r, a_i = random.uniform(-10.0, 10.0), random.uniform(-10.0, 10.0)

                b_r, b_i = random.uniform(-25.0, 25.0), random.uniform(-25.0, 25.0)
                c_r, c_i = random.uniform(-25.0, 25.0), random.uniform(-25.0, 25.0)

                # 2. Solve (Complex Double Precision)
                a, b, c = complex(a_r, a_i), complex(b_r, b_i), complex(c_r, c_i)
                discriminant = b**2 - 4 * a * c
                sqrt_d = cmath.sqrt(discriminant)
                r1 = (-b + sqrt_d) / (2 * a)
                r2 = (-b - sqrt_d) / (2 * a)

                # 3. Write directly to files (Streaming mode)
                coeffs = [a_r, a_i, b_r, b_i, c_r, c_i]
                roots = [r1.real, r1.imag, r2.real, r2.imag]
                
                writer_in.writerow([f"{x:.6f}" for x in coeffs])
                writer_sol.writerow([f"{x:.6f}" for x in (coeffs + roots)])

                # 4. Progress Feedback (every 5000 rows to keep speed up)
                if i % 5000 == 0 or i == args.count:
                    percent = (i / args.count) * 100
                    sys.stdout.write(f"\r  > Progress: {i:,} / {args.count:,} ({percent:.1f}%) ")
                    sys.stdout.flush()

        print(f"\n\nSuccess!")
        print(f"  Inputs: {inputs_path}")
        print(f"  Solved: {solved_path}")

    except KeyboardInterrupt:
        print(f"\nStopped by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()