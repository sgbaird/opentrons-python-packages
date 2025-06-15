# Tailscale GitHub Action Setup

This repository now includes Tailscale GitHub Action integration for secure SSH access to OT-2 simulators during CI workflows.

## Setup

### 1. Required Secrets

Add the following secrets to your GitHub repository:

- `TS_OAUTH_CLIENT_ID`: Tailscale OAuth Client ID
- `TS_OAUTH_SECRET`: Tailscale OAuth Secret  
- `OT2_SIMULATOR_SSH`: OT-2 simulator hostname (format: `hostname` without @ prefix)

### 2. Tailscale OAuth Setup

1. Go to [Tailscale Admin Console](https://login.tailscale.com/admin/settings/keys)
2. Create a new OAuth client
3. Configure appropriate ACL tags (recommended: `tag:ci`)
4. Copy the Client ID and Secret to GitHub repository secrets

### 3. Workflows with Tailscale Support

#### OT-2 Package Testing Workflow

**File**: `.github/workflows/test-ot2-connection.yaml`

Manually triggered workflow for testing package installation on OT-2:

```bash
# Trigger via GitHub UI or API
# Can specify package to test (defaults to 'prefect')
```

**Features**:
- Connects to OT-2 via Tailscale
- Tests package installation from wheels repository
- Validates basic functionality for known packages (prefect, pendulum, pandas)
- Provides detailed system information

#### Build and Deploy with OT-2 Testing

**File**: `.github/workflows/build-and-deploy.yaml`

Extended build workflow with optional OT-2 testing:

```bash
# Enable OT-2 testing when manually triggering the workflow
# Set 'test_ot2' input to true
```

**Features**:
- Builds packages normally
- Optionally tests newly built wheels on OT-2
- Only runs when build succeeds and testing is explicitly enabled

## Usage

### Manual Testing

1. Go to **Actions** tab in GitHub
2. Select **OT-2 Package Testing** workflow
3. Click **Run workflow**
4. Specify package to test (optional, defaults to 'prefect')
5. Monitor results in the workflow logs

### Automated Testing

1. Go to **Actions** tab in GitHub  
2. Select **Build and Deploy Packages** workflow
3. Click **Run workflow**
4. Set **Test OT-2 connection after build** to `true`
5. Workflow will build packages and test them on OT-2

## Troubleshooting

### Connection Issues

- Verify Tailscale OAuth credentials are correct
- Check that OT-2 hostname is reachable via Tailscale network
- Ensure SSH key authentication is properly configured

### Package Installation Issues

- Check that compatible wheels exist in `wheels/` directory
- Verify OT-2 has sufficient disk space
- Review Python/pip compatibility on OT-2 system

### Workflow Failures

- Check GitHub Actions logs for detailed error messages
- Verify all required secrets are configured
- Ensure Tailscale ACL allows CI tag access

## Security Notes

- OAuth credentials provide limited, time-bound access
- CI tag restricts access to authorized operations only
- SSH connections use strict host key checking disabled for automation
- Secrets are properly masked in workflow logs

## Reference

- [Tailscale GitHub Action Documentation](https://tailscale.com/kb/1276/tailscale-github-action)
- [GitHub Actions Setup Steps](https://gh.io/copilot/actions-setup-steps)