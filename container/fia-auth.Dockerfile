FROM python:3.12-slim

WORKDIR /fia_auth

# Install fia_api to the container
COPY . /fia_auth
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir .

CMD ["uvicorn", "fia_auth.app:main", "--host", "0.0.0.0", "--port", "80"]