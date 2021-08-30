ARG VERSION=3.9.1-slim

FROM python:$VERSION AS builder

WORKDIR /opt/app/

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.1.4

RUN pip install "poetry==$POETRY_VERSION"

RUN apt-get update && apt-get install -y git gcc g++ unixodbc-dev

COPY poetry.lock .
COPY poetry.toml .
COPY pyproject.toml .

RUN poetry install --no-dev --no-root

ENV PATH="/opt/app/.venv/bin:$PATH"

FROM python:$VERSION

COPY --from=builder /opt/app/.venv /opt/app/.venv

RUN apt-get update && apt-get install -y curl gnupg

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

COPY ./yc_autodeploy opt/app
WORKDIR opt/app

ENV PATH="/opt/app/.venv/bin:$PATH" \
    PYTHONPATH="/opt/app:$PYTHONPATH" \
    LC_ALL="ru_RU.UTF-8" \
    PYTHONIOENCODING="utf-8"

RUN useradd -g users appuser
USER appuser

CMD ["python", "yc_autodeploy/main.py"]
