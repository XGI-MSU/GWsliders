FROM python:3.9-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /app

COPY --chown=user requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app

# Use Hugging Face’s dynamic port ($PORT)
CMD voila app.ipynb --no-browser --port=${PORT:-7860} --Voila.ip=0.0.0.0
