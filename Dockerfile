# Use a lightweight Python base
FROM python:3.10-slim

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the notebook and other files
COPY --chown=user . /app

# Run Voila on the correct IP/port for Hugging Face Spaces
# $PORT is automatically set by Spaces
ENTRYPOINT ["voila", "app.ipynb", "--no-browser", "--Voila.ip=0.0.0.0"]
CMD ["--port=7860"]

