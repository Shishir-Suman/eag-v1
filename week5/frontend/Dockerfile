FROM python:3.11-slim

WORKDIR /app

# Copy the frontend files
COPY . .

# Install dependencies if any
RUN pip install --no-cache-dir fastapi uvicorn

# Run the frontend server
CMD ["python", "server.py"] 