ARG VERSION=3.9.1-alpine

FROM python:$VERSION AS builder

WORKDIR /opt/app/

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

ENV PATH="/opt/app/.venv/bin:$PATH"

FROM python:$VERSION

COPY --from=builder /opt/app/.venv /opt/app/.venv

COPY ./yc_autodeploy opt/app/yc_autodeploy

WORKDIR opt/app/yc_autodeploy

ENV PATH="/opt/app/.venv/bin:$PATH" \
    PYTHONPATH="/opt/app:$PYTHONPATH" \
    LC_ALL="ru_RU.UTF-8" \
    PYTHONIOENCODING="utf-8"

ENTRYPOINT ["python", "./main.py"]
