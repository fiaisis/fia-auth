FROM python:3.13-slim@sha256:ae9f9ac89467077ed1efefb6d9042132d28134ba201b2820227d46c9effd3174

WORKDIR /fia_auth

# Install fia_api to the container
COPY . /fia_auth
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir .


CMD ["uvicorn", "fia_auth.fia_auth:app", "--host", "0.0.0.0", "--port", "80"]