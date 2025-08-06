FROM python:3.12.4-slim-bookworm
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    apt-get update && \
    apt-get --no-install-recommends install -y curl && \
    apt-get --no-install-recommends install -y tzdata && \
    ln -snf /usr/share/zoneinfo/America/Guayaquil /etc/localtime && \
    echo America/Guayaquil > /etc/timezone && \
    apt-get clean
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]