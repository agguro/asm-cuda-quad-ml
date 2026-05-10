#!/bin/bash

# --- Path Intelligence ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if we are in /test/ or /root/
if [ -f "$SCRIPT_DIR/../meson.build" ]; then
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
    # If the script is in /test/, we want the CSVs to stay here
    TEST_DATA_DIR="$SCRIPT_DIR"
else
    PROJECT_ROOT="$SCRIPT_DIR"
    # If running from root, look for a /test folder or create one
    TEST_DATA_DIR="$PROJECT_ROOT/test"
    mkdir -p "$TEST_DATA_DIR"
fi

# Paths
BUILD_DIR="$PROJECT_ROOT/builddir"
SOLVER_BIN="$BUILD_DIR/src/x86_64/quadratic_solver"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# Moved CSVs to the TEST_DATA_DIR
INPUTS_CSV="$TEST_DATA_DIR/inputs.csv"
GPU_RESULTS="$TEST_DATA_DIR/gpu_results.csv"
REFERENCE_RESULTS="$TEST_DATA_DIR/reference_results.csv"

echo "--- Full Rebuild & Test Pipeline (Clean Root Mode) ---"

# --- 1. Build Section ---
cd "$PROJECT_ROOT" || exit
if [ -d "$BUILD_DIR" ]; then
    echo "[1/6] Cleaning build..."
    rm -rf "$BUILD_DIR"
fi

echo "[2/6] Configuring Meson..."
meson setup "$BUILD_DIR" > /dev/null

echo "[3/6] Compiling..."
meson compile -C "$BUILD_DIR" > /dev/null

# --- 2. Data Generation ---
echo "[4/6] Generating equations in $TEST_DATA_DIR..."
python3 "$SCRIPTS_DIR/generate_equations.py" 50000 --output "$INPUTS_CSV"

date
# --- 3. Execution ---
echo "[5/6] Executing GPU Solver..."
"$SOLVER_BIN" "$INPUTS_CSV" -o "$GPU_RESULTS"
date

# --- 4. Verification ---
echo "[6/6] Verifying results..."
python3 "$SCRIPTS_DIR/verify_results.py" "$INPUTS_CSV" > "$REFERENCE_RESULTS"

echo ""
python3 "$SCRIPTS_DIR/fuzzy_diff.py" "$REFERENCE_RESULTS" "$GPU_RESULTS"

if [ $? -eq 0 ]; then
    echo "VERDICT: SUCCESS. Build is stable and math is accurate."
else
    echo "VERDICT: FAILURE. Check for ABI/alignment issues or math errors."
fi

echo "--- Pipeline Complete ---"