#!/bin/bash
# Install script for OT-2 Python packages
# Usage: curl -sSL https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/install.sh | bash -s -- PACKAGE_NAME

set -e

PACKAGE_NAME=${1:-}
REPO_URL="https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels"
TEMP_DIR="/tmp/opentrons-packages"

if [ -z "$PACKAGE_NAME" ]; then
    echo "Usage: $0 PACKAGE_NAME"
    echo ""
    echo "Available packages:"
    echo "  pandas      - Data analysis library"
    echo "  prefect     - Workflow orchestration framework"
    echo "  pendulum    - Date/time manipulation library (Prefect dependency)"
    echo ""
    echo "Example:"
    echo "  $0 pandas"
    echo "  $0 prefect"
    echo "  $0 pendulum"
    exit 1
fi

mkdir -p "$TEMP_DIR"

case "$PACKAGE_NAME" in
    "pandas")
        WHEEL_FILE="pandas-1.5.0-cp310-cp310-linux_armv7l.whl"
        ;;
    "prefect")
        WHEEL_FILE="prefect-3.3.4-py3-none-any.whl"
        ;;
    "pendulum")
        # Use universal wheel by default (more compatible)
        WHEEL_FILE="pendulum-3.1.0-py3-none-any.whl"
        echo "Note: Installing universal pendulum wheel. For better performance on ARM64, use:"
        echo "  curl -L $REPO_URL/pendulum-3.1.0-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl -o /tmp/pendulum.whl && pip install /tmp/pendulum.whl"
        ;;
    *)
        echo "Error: Unknown package '$PACKAGE_NAME'"
        exit 1
        ;;
esac

echo "Downloading $PACKAGE_NAME..."
curl -L "$REPO_URL/$WHEEL_FILE" -o "$TEMP_DIR/$WHEEL_FILE"

echo "Installing $PACKAGE_NAME..."
pip install "$TEMP_DIR/$WHEEL_FILE"

echo "Cleaning up..."
rm -f "$TEMP_DIR/$WHEEL_FILE"

echo "Successfully installed $PACKAGE_NAME!"