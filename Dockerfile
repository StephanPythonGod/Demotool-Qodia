# Use the official Python base image
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-deu \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set the Poetry path as an environment variable
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the project files
COPY pyproject.toml poetry.lock ./
COPY app.py ./
COPY utils ./utils
COPY data ./data
COPY schemas ./schemas
COPY models ./models

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev --no-root -vvv

# Check if the flair model already exists in the models directory
# If it does not, download the model
RUN test -f ./models/flair-ner-german-large.pt || \
    python -c "from flair.models import SequenceTagger; SequenceTagger.load('flair/ner-german-large')"

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variables
ENV PORT=8080
ENV DEPLOYMENT_ENV=local

# Start the Streamlit application
CMD ["poetry", "run", "streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]