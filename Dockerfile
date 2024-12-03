# Use the official Python 3.9 image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and application code
COPY requirements.txt .
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your application listens on
EXPOSE 6000

# Command to run your application
CMD ["python", "main.py"]
