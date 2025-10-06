FROM python:3.10.12-slim-bookworm

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY . .

RUN poetry sync --only main

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "bgtorrent_observer.app:app", "--host", "0.0.0.0", "--port", "8000"]
