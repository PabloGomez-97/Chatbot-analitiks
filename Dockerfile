# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Flask will run on
EXPOSE 8080

# Set environment variables to ensure output is sent straight to the terminal
ENV PYTHONUNBUFFERED=1

# Run the command to start the Flask app
CMD ["python", "receive.py"]
