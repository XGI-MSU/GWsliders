FROM python:3.9-slim

# Create non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements
COPY --chown=user requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

# Copy app files
COPY --chown=user . /app

# Run Voila on the correct port and IP for Hugging Face
ENTRYPOINT ["voila", "app.ipynb", "--no-browser", "--Voila.ip=0.0.0.0"]
CMD ["--port=7860"]
