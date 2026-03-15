# Use a lightweigh Python image
FROM python:3.11-slim

# set the working directory
WORKDIR /app

# Copy only requirements first to use Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
Copy . .

# Expose the port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]