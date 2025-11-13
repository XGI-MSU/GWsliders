# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.9
FROM python:3.9

# Create non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install dependencies
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy app files
COPY --chown=user . /app

# Run Voila (default to port 7860 if $PORT is not set)
CMD bash -c "voila app.ipynb --port=${PORT:-7860} --no-browser --strip_sources=True --Voila.ip=0.0.0.0"

