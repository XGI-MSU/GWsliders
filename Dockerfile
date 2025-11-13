FROM python:3.10-bullseye

# Install system build tools
RUN apt-get update && apt-get install -y \
    build-essential python3-dev libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir early
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install everything as root so packages are in /usr/local
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

# Create non-root user for runtime
RUN useradd -m -u 1000 user
USER user

# Copy notebook and data (owned by user)
COPY --chown=user:user . /app

# Run Voila
ENTRYPOINT ["voila", "notebook.ipynb", "--no-browser", "--Voila.ip=0.0.0.0"]
CMD ["--port=7860"]





