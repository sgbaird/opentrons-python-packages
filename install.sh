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
    echo "  prefect     - Workflow orchestration (placeholder)"
    echo ""
    echo "Example:"
    echo "  $0 pandas"
    exit 1
fi

mkdir -p "$TEMP_DIR"

case "$PACKAGE_NAME" in
    "pandas")
        WHEEL_FILE="pandas-1.5.0-cp310-cp310-linux_armv7l.whl"
        ;;
    "prefect")
        echo "Error: Prefect wheel is not yet available. Please check CI builds or releases."
        exit 1
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