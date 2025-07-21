#!/bin/bash
# Prefect Cloud Setup Script
if [ $# -ne 2 ]; then
    echo "Usage: $0 <api_key> <workspace_url>"
    echo "Example: $0 \"pnb_xxx...\" \"https://api.prefect.cloud/api/accounts/xxx/workspaces/xxx\""
    exit 1
fi

API_KEY="$1"
WORKSPACE_URL="$2"

echo "Setting up Prefect Cloud authentication..."
mkdir -p /root/.prefect

cat > /root/.prefect/profiles.toml << PROFILEEOF
active = "cloud"

[profiles.cloud]
PREFECT_API_KEY = "${API_KEY}"
PREFECT_API_URL = "${WORKSPACE_URL}"
PROFILEEOF

echo "✅ Prefect Cloud profile configured"
echo "Testing cloud connectivity..."

source /root/setup_prefect_env.sh
python3 /root/cloud_test.py

echo "Prefect Cloud setup complete!"