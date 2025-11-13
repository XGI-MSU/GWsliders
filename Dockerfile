FROM python:3.10-slim

# Install system dependencies for building wheels
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy notebook and other files
COPY --chown=user . /app

# Run Voila
ENTRYPOINT ["voila", "notebook.ipynb", "--no-browser", "--Voila.ip=0.0.0.0"]
CMD ["--port=7860"]


