# Prefect 3.3.4 Support for OT-2

This directory contains the build configuration for Prefect 3.3.4, a workflow orchestration tool, compiled for the Opentrons OT-2 robot.

## Package Information

- **Package**: Prefect
- **Version**: 3.3.4
- **Source**: GitHub repository PrefectHQ/prefect
- **Build Type**: Pure Python package with compiled dependencies

## Build Configuration

The `build.py` file configures the build system to:

1. Download Prefect 3.3.4 source code from GitHub (tag `3.3.4`)
2. Build a wheel package using `bdist_wheel` command
3. Cross-compile for arm7hf architecture (OT-2 compatible)

## Dependencies with Native Components

Prefect has several runtime dependencies that include compiled components:

- `asyncpg` - PostgreSQL adapter with C extensions
- `cryptography` - Cryptographic library with native code
- `orjson` - Fast JSON library with Rust extensions  
- `pydantic-core` - Pydantic validation core with Rust extensions
- `ujson` - Fast JSON library with C extensions
- `websockets` - WebSocket library with C extensions

These dependencies are handled automatically by the build system and will be resolved from the package index or built separately if needed.

## Build Process

To build this package:

```bash
./build-packages --verbose --build-type packages-only
```

Or to build the package and generate a package index:

```bash
./build-packages --verbose --build-type both
```

The build system will:
1. Pull the Prefect source code from GitHub
2. Set up a cross-compilation environment using Buildroot SDK
3. Create a Python virtual environment with build dependencies
4. Build the wheel package for arm7hf architecture
5. Output the wheel to the dist/ directory
6. Generate a PEP 503 package index (if using `--build-type both`)

## Installation on OT-2

### Generic Instructions

Once built and deployed, the package can be installed on an OT-2 using:

```bash
pip install prefect --index-url <opentrons-package-index-url>
```

### Specific Instructions for sgbaird/opentrons-python-packages

For this specific fork, once the build system is deployed:

1. **Development builds**: Packages built from branches will be available at:
   ```bash
   pip install prefect --index-url https://dev.pypi.opentrons.com/[branch-name]/simple/
   ```

2. **For the current branch** (`copilot/fix-1`):
   ```bash
   pip install prefect --index-url https://dev.pypi.opentrons.com/copilot/fix-1/simple/
   ```

3. **Production builds**: Once merged and tagged with `packages@v*`, packages will be available at:
   ```bash
   pip install prefect --index-url http://pypi.opentrons.com/simple/
   ```

**Note**: The URLs above assume the same deployment infrastructure as the upstream repository. If deploying to different infrastructure, replace the base URLs accordingly.

## Notes

- Prefect is primarily a pure Python package, so the build should be straightforward
- The build system will handle cross-compilation of any C/Rust extensions in dependencies
- The package has been tested for syntax and import validation
- Network connectivity is required during the build process to download source code