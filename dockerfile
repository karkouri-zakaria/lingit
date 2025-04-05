# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies and Git
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

# Clone the repository
RUN git clone https://github.com/karkouri-zakaria/learndeutsch.git /app

# Set the working directory
WORKDIR /app

# Create a virtual environment
RUN python3 -m venv $VIRTUAL_ENV

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit uses
EXPOSE 8501

# Command to run your script
CMD ["python", "run.py"]
