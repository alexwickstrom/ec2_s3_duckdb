# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY Pipfile Pipfile.lock /app/
WORKDIR /app
RUN pip install pipenv && pipenv install --system --deploy

# Copy the current directory contents into the container at /app
COPY . /app/

RUN chmod +x /app/entrypoint.sh

# Run entrypoint.sh when the container launches
CMD ["/app/entrypoint.sh"]
