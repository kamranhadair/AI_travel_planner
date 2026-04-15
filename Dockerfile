# Base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set the working directory
WORKDIR /app

# Install dependencies needed for our backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source code
COPY backend/ /app/backend/

# Copy the frontend static files so FastAPI can serve them
COPY frontend/ /app/frontend/

# Expose the API port
EXPOSE 8000

# Set the working directory to the backend so 'app.main' module route works naturally
WORKDIR /app/backend

# Command to run the Uvicorn server in production mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
