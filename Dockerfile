# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create a virtual environment
RUN python3 -m venv $VIRTUAL_ENV

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . /app

# Set the working directory
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Command to run your script
CMD ["python", "run.py"]

EXPOSE 8501