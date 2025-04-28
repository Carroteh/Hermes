# Use the official Python 3.13.1 slim image as the base
FROM python:3.13.1-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Poetry and Python
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=2.0.1
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION
ENV PATH="/root/.local/bin:$PATH"

# Copy Poetry configuration files
COPY pyproject.toml poetry.lock /app/

# Configure Poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Install main dependencies
RUN poetry install --no-root --only main

# Install dev dependencies (for tests)
RUN poetry install --no-root --only dev

# Copy the rest of the project files
COPY . /app

# Set PYTHONPATH to include /app/src
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Command to run main.py
CMD ["poetry", "run", "python", "src/hermes/main.py"]