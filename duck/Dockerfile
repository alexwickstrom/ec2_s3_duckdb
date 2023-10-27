# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app
COPY ./app/Pipfile ./app/Pipfile.lock /app/

# Install DuckDB
RUN pip install pipenv && pipenv install ipython --system --deploy

# Run shell by default
CMD [ "bash" ]
