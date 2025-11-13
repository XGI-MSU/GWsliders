FROM python:3.10-slim

# Install system build tools
RUN apt-get update && apt-get install -y \
    build-essential python3-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 user
WORKDIR /app

# Copy requirements and install everything as root
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
        voila>=0.5,<0.7 \
        ipywidgets>=8.0 \
        ipympl==0.9.4 \
        notebook>=6.5 \
        matplotlib==3.8.1

# Enable nbextensions as root
RUN jupyter nbextension install --py widgetsnbextension --sys-prefix \
    && jupyter nbextension enable --py widgetsnbextension --sys-prefix \
    && jupyter nbextension enable --py ipympl --sys-prefix \
    && jupyter serverextension enable --py voila --sys-prefix

# Copy notebook and data
COPY . /app

# Switch to non-root user for runtime
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Run Voila
ENTRYPOINT ["voila", "notebook.ipynb", "--no-browser", "--Voila.ip=0.0.0.0"]
CMD ["--port=7860"]




