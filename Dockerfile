FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
RUN pip install uv && uv sync --frozen --no-dev
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "delve.main:app", "--host", "0.0.0.0", "--port", "8000"]
