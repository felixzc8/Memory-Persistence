FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY backend/pyproject.toml backend/uv.lock* ./
COPY TiMemory/ ../TiMemory/

RUN uv sync

COPY backend/ .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]