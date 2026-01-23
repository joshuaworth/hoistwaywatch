FROM python:3.12-slim

WORKDIR /app

# OpenCV runtime deps (headless)
RUN apt-get update -y \
  && apt-get install -y --no-install-recommends libglib2.0-0 libgl1 \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE /app/
COPY src /app/src
COPY configs /app/configs

RUN python -m pip install -U pip \
  && python -m pip install .

ENV PYTHONUNBUFFERED=1

