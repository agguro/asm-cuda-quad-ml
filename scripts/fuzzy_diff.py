#!/usr/bin/env python3
import sys

def fuzzy_match(file1, file2, tolerance=0.0002):
    with open(file1) as f1, open(file2) as f2:
        for i, (line1, line2) in enumerate(zip(f1, f2), 1):
            v1 = [float(x) for x in line1.strip().split(',')]
            v2 = [float(x) for x in line2.strip().split(',')]
            
            for a, b in zip(v1, v2):
                if abs(a - b) > tolerance:
                    print(f"Mismatch at line {i}: {a} vs {b}")
                    return False
    return True

if __name__ == "__main__":
    if fuzzy_match(sys.argv[1], sys.argv[2]):
        print("SUCCESS: All results match within tolerance.\n")
        sys.exit(0)
    else:
        sys.exit(1)