FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (curl for healthchecks/debugging)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Scrapy project
COPY scrapy.cfg ./
COPY ecommerce ./ecommerce
COPY page.html ./

# Default to running a specific spider; override with docker run/cmp
ENTRYPOINT ["scrapy"]
CMD ["crawl", "nike"]
