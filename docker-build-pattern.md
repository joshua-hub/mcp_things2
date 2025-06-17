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
1. Start with same slim Python base image
2. Update and upgrade OS packages for security:
   - apt-get update
   - apt-get upgrade
3. Install minimal runtime dependencies
4. Clean up package caches and lists
5. Create non-privileged user and group
6. Set up application directory with proper ownership
7. Copy only the virtual environment from builder stage
8. Set correct permissions on copied files
9. Switch to non-privileged user
10. Copy application code
11. Use full path to Python interpreter from venv

## Security Considerations
- Updated OS packages in final image only
- No build tools in final image
- No pip.conf in final image
- Non-root execution
- Minimal system packages
- Explicit file ownership
- Clean package caches and lists

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

FROM python:3.9-slim
# Update OS and install runtime dependencies
RUN apt-get update && apt-get upgrade -y
# Setup runtime environment
# Copy only venv from builder
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