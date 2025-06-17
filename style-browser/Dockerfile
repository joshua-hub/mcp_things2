# Stage 1: Builder
FROM python:3.11-alpine AS builder

# Update package lists and install build dependencies
RUN apk update && \
    apk add --no-cache python3-dev gcc musl-dev && \
    rm -rf /var/cache/apk/*

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
FROM python:3.11-alpine

# Install minimal runtime dependencies and create user
RUN apk add --no-cache libstdc++ && \
    # Create non-privileged user
    addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    # Create application directory
    mkdir -p /app/workspace && \
    chown -R appuser:appgroup /app && \
    # Remove unnecessary packages and shells
    rm -f /bin/sh /bin/ash /bin/bash && \
    rm -rf /bin/* /sbin/* /usr/bin/* /usr/sbin/*

# Copy virtual environment from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Clean up Python artifacts
RUN find /venv -type f -name "*.so" -exec strip {} \; 2>/dev/null || true && \
    find /venv -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true && \
    find /venv -type f -name "*.pyc" -delete && \
    find /venv -type d -name "*.dist-info" -exec rm -r {} + 2>/dev/null || true && \
    find /venv -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true && \
    find /venv -type d -name "doc" -exec rm -r {} + 2>/dev/null || true && \
    find /venv -type d -name "docs" -exec rm -r {} + 2>/dev/null || true

# Copy application files
COPY --chown=appuser:appgroup server.py index.html /app/

# Switch to non-privileged user
USER appuser

# Expose port
EXPOSE 8080

# Run the application using full path to Python interpreter
CMD ["/venv/bin/python", "/app/server.py"] 