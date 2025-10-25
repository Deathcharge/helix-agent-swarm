# Dockerfile for Helix Collective Streamlit Deployment
# Based on Python 3.11 for compatibility with the project's Python version

# Use the official Python image as the base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PORT 8501

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the Streamlit port
EXPOSE 8501

# Command to run the Streamlit application
# The Streamlit application file is helix_multi_model_chat.py
CMD ["streamlit", "run", "helix_multi_model_chat.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

