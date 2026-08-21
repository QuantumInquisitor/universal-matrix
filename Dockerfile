version: '3.8'

services:
  matrix-engine:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: universal_matrix_engine
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 10s
      timeout: 5s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    container_name: matrix_prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    depends_on:
      - matrix-engine
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: matrix_grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: unless-stopped