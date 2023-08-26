# Use the official Python 3.11 image from DockerHub
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies & Tesseract
RUN apt-get update -y && \
    # Get teseract-ocr & curl
    apt-get install -y tesseract-ocr tesseract-ocr-eng libtesseract-dev && \ 
    # Curl & essentials
    apt-get install -y curl build-essential && \
    # Get OpenCV dependencies
    apt-get -y install ffmpeg libsm6 libxext6 && \
    apt-get clean && \
    apt-get autoremove

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the local requirements file to the container
COPY ./requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local app directory contents to the container
COPY . .

# Copy the entrypoint script to the container
RUN chmod +x ./entrypoint.sh

# Expose port 8000 to the outer world (for gunicorn/flask)
EXPOSE 8000

# The command to run our application using Gunicorn
CMD ["./entrypoint.sh"]