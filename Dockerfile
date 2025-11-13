# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.9

# Add a user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install dependencies
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy app files
COPY --chown=user . /app

# Serve the notebook with Voila instead of uvicorn
CMD ["voila", "app.ipynb", "--port=$PORT", "--no-browser", "--strip_sources=True", "--Voila.ip=0.0.0.0"]


