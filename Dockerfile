# Build Frontend
FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build Backend
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
# Add sqlalchemy for persistence
RUN pip install --no-cache-dir -r requirements.txt sqlalchemy

# Copy backend code
COPY backend/ ./backend

# Copy built frontend assets to backend static folder
# We'll serve these via FastAPI for simplicity as per plan
COPY --from=frontend-build /app/frontend/build ./backend/static

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
