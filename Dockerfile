ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim-bookworm

RUN set -eux; apt-get update \
&& apt-get install --no-install-recommends -y build-essential \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY dist/ /app/dist/
RUN set -eux; \
LATEST=$(ls -t /app/dist/*.whl | head -n1); \
pip install --no-cache-dir "$LATEST"; \
rm -rf /app/dist/

CMD ["python", "-c", "print('Container started successfully!')"]
