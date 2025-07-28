FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock* ./
RUN uv sync

COPY . .

CMD ["uv", "run", "celery", "-A", "celery_app", "worker", "--loglevel=info", "--reload"]