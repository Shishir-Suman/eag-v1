FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using uv sync
RUN pip install --no-cache-dir uv && \
    uv sync

# Copy the rest of the application
COPY . .

# Run the application
CMD ["uv", "run", "python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 