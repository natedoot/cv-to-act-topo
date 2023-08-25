# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Install necessary packages
RUN pip install --trusted-host pypi.python.org cloudvision grpcio pyyaml

# Copy the local code to the container
COPY ./scripts /app

# Make the scripts executable
RUN chmod +x /app/*.py
