# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 8255

# Define environment variable
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run main.py when the container launches
CMD ["python", "-u", "src/main.py"]
#CMD ["flask", "run", "--host=0.0.0.0"]