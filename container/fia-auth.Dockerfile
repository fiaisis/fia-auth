FROM python:3.13-slim@sha256:2ec5a4a5c3e919570f57675471f081d6299668d909feabd8d4803c6c61af666c

WORKDIR /fia_auth

# Install fia_api to the container
COPY . /fia_auth
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir .


CMD ["uvicorn", "fia_auth.fia_auth:app", "--host", "0.0.0.0", "--port", "80"]