FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy project files
COPY pyproject.toml .
# If you have uv.lock, uncomment the next line
# COPY uv.lock .

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application code
COPY src/ src/

# Expose the port for SSE
EXPOSE 3000

# Run the server
CMD ["uv", "run", "uvicorn", "mytravaly_mcp.server:app", "--host", "0.0.0.0", "--port", "3000"]
