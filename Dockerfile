
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

WORKDIR /app

# Dependências necessárias para o OpenCV e RapidOCR
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libgl1 \
       libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ocr_worker.py ./

RUN useradd -m appuser
USER appuser

CMD ["sh", "-c", "exec gunicorn app:app --bind 0.0.0.0:${PORT:-10000} --workers 1 --threads 1 --timeout 180 --max-requests 30 --max-requests-jitter 5 --access-logfile - --error-logfile -"]
