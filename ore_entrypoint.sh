#!/bin/bash
set -e

echo "================================================"
echo "ORE Analytics Application"
echo "================================================"

# Check if ORE is installed
if [ ! -f "/usr/local/bin/ore" ]; then
    echo "ERROR: ORE executable not found!"
    exit 1
fi

echo "✓ ORE executable found at: /usr/local/bin/ore"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found!"
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"

# Check if required directories exist
for dir in /app/ore_input /app/ore_output /app/data; do
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir"
    fi
done

echo "✓ Required directories verified"

# Check if pandas is installed (verify Python dependencies)
if ! python3 -c "import pandas" 2>/dev/null; then
    echo "ERROR: Required Python packages not installed!"
    echo "Installing requirements..."
    pip3 install -r /app/requirements.txt
fi

echo "✓ Python dependencies verified"

# Display environment variables
echo ""
echo "Configuration:"
echo "  ORE_EXECUTABLE: ${ORE_EXECUTABLE:-/usr/local/bin/ore}"
echo "  INPUT_DIR: ${INPUT_DIR:-/app/ore_input}"
echo "  OUTPUT_DIR: ${OUTPUT_DIR:-/app/ore_output}"
echo "  LOG_LEVEL: ${LOG_LEVEL:-INFO}"
echo ""

# Check if there are any input files
input_count=$(ls -1 "${INPUT_DIR:-/app/ore_input}" 2>/dev/null | wc -l)
if [ "$input_count" -eq 0 ]; then
    echo "⚠ Warning: No input files found in ${INPUT_DIR:-/app/ore_input}"
    echo "  The application will create sample input files."
fi

echo "================================================"
echo "Starting application..."
echo "================================================"
echo ""

# Execute the command passed to the container
exec "$@"
