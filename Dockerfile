# Use Python base image
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Set working directory
WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (without installing the project itself)
# This layer will be cached unless dependencies change
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy the rest of the application code
COPY main.py ./
COPY gdrive_backup ./gdrive_backup

# Install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Set the virtual environment in PATH for direct command execution
ENV PATH="/app/.venv/bin:$PATH"

# Default token path for containerized environment
ENV TOKEN_PATH="/gdrive_backup/token.json"
ENV GOOGLE_CREDENTIALS_PATH="/gdrive_backup/credentials.json"

# Run the backup script
CMD ["python", "main.py"]
