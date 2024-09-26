FROM python:3.12-slim@sha256:15bad989b293be1dd5eb26a87ecacadaee1559f98e29f02bf6d00c8d86129f39

WORKDIR /fia_auth

# Install fia_api to the container
COPY . /fia_auth
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir .


CMD ["uvicorn", "fia_auth.fia_auth:app", "--host", "0.0.0.0", "--port", "80"]