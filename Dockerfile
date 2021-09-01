ARG VERSION=3.9.1-alpine

FROM python:$VERSION AS builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.1.4

RUN apk update && apk add gcc git g++ unixodbc-dev musl-dev python3-dev libffi-dev openssl-dev cargo

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock .
COPY poetry.toml .
COPY pyproject.toml .

RUN poetry install --no-dev --no-root

ENV PATH="/.venv/bin:$PATH"

FROM python:$VERSION

COPY --from=builder /.venv /.venv

COPY ./yc_autodeploy /yc_autodeploy

ENV PATH="/.venv/bin:$PATH" \
    PYTHONPATH="/:$PYTHONPATH" \
    LC_ALL="ru_RU.UTF-8" \
    PYTHONIOENCODING="utf-8"

ENTRYPOINT ["python", "/yc_autodeploy/main.py"]
