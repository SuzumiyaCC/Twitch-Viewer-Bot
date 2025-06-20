FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    CHROME_BIN=/snap/bin/chromium \
    CHROMEDRIVER=/usr/lib/chromium-browser/chromedriver

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        snapd \
        chromium-browser \
        chromium-chromedriver && \
    snap install chromium && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
