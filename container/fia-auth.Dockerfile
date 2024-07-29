FROM python:3.12-slim@sha256:740d94a19218c8dd584b92f804b1158f85b0d241e5215ea26ed2dcade2b9d138

WORKDIR /fia_auth

# Install fia_api to the container
COPY . /fia_auth
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir .


CMD ["uvicorn", "fia_auth.fia_auth:app", "--host", "0.0.0.0", "--port", "80"]