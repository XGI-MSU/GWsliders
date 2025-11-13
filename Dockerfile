FROM python:3.10-slim

# Install system build tools
RUN apt-get update && apt-get install -y \
    build-essential python3-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements and install everything in one step
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy notebook and data
COPY --chown=user . /app

# Switch to root to enable nbextensions
USER root
RUN jupyter nbextension install --py widgetsnbextension --sys-prefix
RUN jupyter nbextension enable --py widgetsnbextension --sys-prefix
RUN jupyter nbextension enable --py ipympl --sys-prefix
RUN jupyter serverextension enable --py voila --sys-prefix

# Switch back to non-root user
USER user

# Run Voila
ENTRYPOINT ["voila", "notebook.ipynb", "--no-browser", "--Voila.ip=0.0.0.0"]
CMD ["--port=7860"]



