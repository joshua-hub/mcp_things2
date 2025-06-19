# Stage 1: Builder
FROM python:3.11-slim AS builder

# Update package lists and install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up pip configuration
RUN mkdir -p /root/.pip
COPY pip.conf /root/.pip/pip.conf

# Create and activate virtual environment
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final
FROM python:3.11-slim

# Install minimal runtime dependencies and create user
RUN apt-get update && \
    apt-get install -y --no-install-recommends libstdc++6 && \
    # Create non-privileged user
    groupadd -r appgroup && \
    useradd -r -g appgroup -d /app appuser && \
    # Create application directory
    mkdir -p /app/workspace && \
    chown -R appuser:appgroup /app && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Clean up Python artifacts
RUN find /venv -type f -name "*.so" -exec strip {} \; 2>/dev/null || true && \
    find /venv -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true && \
    find /venv -type f -name "*.pyc" -delete && \
    find /venv -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true && \
    find /venv -type d -name "doc" -exec rm -r {} + 2>/dev/null || true && \
    find /venv -type d -name "docs" -exec rm -r {} + 2>/dev/null || true

# Copy application files
COPY --chown=appuser:appgroup app/ /app/app/

# Create mount points for models and styles
RUN mkdir -p /app/models /app/sdxl_styles && \
    chown -R appuser:appgroup /app/models /app/sdxl_styles

# Switch to non-privileged user
USER appuser

# Expose port
EXPOSE 8000

# Run the application using full path to Python interpreter
CMD ["/venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 