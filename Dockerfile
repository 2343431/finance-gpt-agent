# Dockerfile

FROM python:3.9-slim

# Set unbuffered mode for Python
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements_complete.txt .
RUN pip install --no-cache-dir -r requirements_complete.txt

# Copy the application code
COPY . .

# Expose ports
EXPOSE 8000
EXPOSE 8501
