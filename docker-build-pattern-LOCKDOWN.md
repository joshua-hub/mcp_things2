# Python Docker Build Pattern

This document describes a secure, efficient multi-stage build pattern for Python applications.

## Key Features
- Multi-stage build to minimize final image size
- Custom pip configuration for private/proxy PyPI servers
- Python virtual environment
- Non-root user execution
- Clean package caches
- Proper file permissions
- Updated OS packages in final image
- Stripped debug symbols
- Removed Python bytecode
- Removed package documentation
- Minimal Alpine-based image
- No shells or utilities in final image

## Stage 1: Builder
1. Start with a slim Python base image
2. Update package lists only:
   - apt-get update
3. Install minimal build dependencies (python3-venv)
4. Clean up package caches and lists
5. Set up pip configuration:
   - Create /root/.pip directory
   - Copy pip.conf from build context
   - pip.conf is only present in builder stage
6. Create Python virtual environment in /venv
7. Install Python dependencies into venv
8. Clean up package caches

## Stage 2: Final
1. Start with Alpine Python base image
2. Install only essential runtime dependencies
3. Remove all shells and utilities:
   - Remove /bin/sh, /bin/ash, /bin/bash
   - Remove all binaries from /bin, /sbin, /usr/bin, /usr/sbin
4. Create non-privileged user and group
5. Set up application directory with proper ownership
6. Copy only the virtual environment from builder stage
7. Set correct permissions on copied files
8. Remove debug symbols from Python binaries
9. Remove Python bytecode and documentation
10. Switch to non-privileged user
11. Copy application code
12. Use full path to Python interpreter from venv

## Security Considerations
- Updated OS packages in final image only
- No build tools in final image
- No pip.conf in final image
- Non-root execution
- Minimal system packages
- Explicit file ownership
- Clean package caches and lists
- Stripped debug symbols from binaries
- No Python bytecode files
- No package documentation or metadata
- No shells or utilities in final image
- Minimal attack surface with Alpine base

## Performance Optimizations
- Layer caching for dependencies
- Clean package caches
- Minimal image size
- Separate build and runtime concerns
- Efficient package cleanup
- No unnecessary OS updates in builder stage

## Usage Pattern
```dockerfile
# Example structure - not complete
FROM python:3.9-slim AS builder
# Update package lists and install build dependencies
RUN apt-get update
# Setup build environment
# Install dependencies in venv

FROM python:3.9-alpine
# Install minimal runtime dependencies
RUN apk add --no-cache libstdc++ \
    # Remove shells and utilities
    && rm -f /bin/sh /bin/ash /bin/bash \
    && rm -rf /bin/* /sbin/* /usr/bin/* /usr/sbin/* \
    # Setup runtime environment
    && mkdir -p /app/workspace
# Copy only venv from builder
# Remove debug symbols and documentation
RUN find /venv -type f -name "*.so" -exec strip {} \; 2>/dev/null || true \
    && find /venv -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true \
    && find /venv -type f -name "*.pyc" -delete \
    && find /venv -type d -name "*.dist-info" -exec rm -r {} + 2>/dev/null || true \
    && find /venv -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true \
    && find /venv -type d -name "doc" -exec rm -r {} + 2>/dev/null || true \
    && find /venv -type d -name "docs" -exec rm -r {} + 2>/dev/null || true
# Run as non-root user
```

## Notes
- Requires pip.conf in build context
- Virtual environment path: /venv
- Application directory: /app
- Non-root user: appuser:appgroup
- Uses absolute paths to Python interpreter
- Always clean up after package operations
- OS updates only in final image
- Strip debug symbols from Python binaries
- Remove Python bytecode and documentation
- Use Alpine base image for minimal attack surface
- Remove all shells and utilities from final image 