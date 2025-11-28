# fia-auth
[![codecov](https://codecov.io/gh/fiaisis/fia-auth/graph/badge.svg?token=lzm0DS1jhG)](https://codecov.io/gh/fiaisis/fia-auth)
![License: GPL-3.0](https://img.shields.io/github/license/fiaisis/fia-auth)
![Build: passing](https://img.shields.io/github/actions/workflow/status/fiaisis/fia-auth/tests.yml?branch=main)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-30173d)](https://docs.astral.sh/ruff/)
[![linting: ruff](https://img.shields.io/badge/linting-ruff-30173d)](https://docs.astral.sh/ruff/)

A small FastAPI microservice that authenticates users against the User Office Web Service (UOWS), issues short-lived access
JWTs and long-lived refresh tokens, and exposes a minimal internal API to retrieve experiment (RB) numbers for a given
user. The service also determines a user's role (user vs staff) via a local Postgres table and UOWS role lookup.

- Framework: FastAPI + Starlette
- Tokens: HS256 JWTs (PyJWT)
- External deps: UOWS REST API, Proposal Allocations GraphQL API
- Storage: Postgres (only for a lightweight `staff` table)

## Quick start

Prerequisites:
- Python 3.11+
- Postgres reachable (defaults: host `localhost`, db `fia`, port `5432`)
- Network/VPN access to UOWS and Proposal Allocations dev endpoints when using those features

Install and run:

1) Install the package

   pip install -e .

2) Set required environment variables (see Environment below)

3) Start the API locally

   uvicorn fia_auth.fia_auth:app --reload

OpenAPI UI is available at http://127.0.0.1:8000/docs

## API overview

- POST /login
  - Body: {"username": "...", "password": "..."}
  - Authenticates via UOWS, returns an access token in the response body and sets a HttpOnly, Secure refresh_token cookie
  - Response: "<access_jwt>"

- POST /verify
  - Body: {"token": "<access_jwt>"}
  - Verifies signature and expiry; returns "ok" if valid

- POST /refresh
  - Body: {"token": "<access_jwt>"}
  - Cookies: refresh_token=<refresh_jwt>
  - Verifies refresh token and returns a renewed access token

- GET /experiments (internal)
  - Query: user_number=<int>
  - Header: Authorization: Bearer <FIA_AUTH_API_KEY>
  - Returns list[int] of RB numbers for the user via the Proposal Allocations API

Notes:
- The access token lifetime is configurable via ACCESS_TOKEN_LIFETIME_MINUTES (default 10)

## Environment

Required for typical usage:
- JWT_SECRET: Symmetric key used to sign/verify JWTs (default: "shh" — do not use in production)
- UOWS_API_KEY: API key for UOWS calls
- FIA_AUTH_API_KEY: API key value required by the internal /experiments endpoint
- DB_USERNAME: Postgres user (default: postgres)
- DB_PASSWORD: Postgres password (default: password)
- DB_IP: Postgres host/ip (default: localhost)
- UOWS_URL: Base URL for UOWS (default: https://devapi.facilities.rl.ac.uk/users-service)
- ALLOCATIONS_URL: GraphQL endpoint for Proposal Allocations (default: https://devapi.facilities.rl.ac.uk/proposal-allocations/graphql)
- ACCESS_TOKEN_LIFETIME_MINUTES: Access token lifetime in minutes (default: 10)

Database connection string used by the service:

postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:5432/fia

The service uses a single table created by SQLAlchemy:
- staff(id serial primary key, user_number int)

## Running with Docker

A container definition is provided at container/fia-auth.Dockerfile.

Build:

docker build -f container/fia-auth.Dockerfile -t fia-auth:local .

Run:

# Map host 8000 -> container 80
Docker (Linux/macOS):
  docker run --rm -p 8000:80 \
    -e JWT_SECRET=change-me \
    -e UOWS_API_KEY=... \
    -e FIA_AUTH_API_KEY=... \
    -e DB_USERNAME=postgres -e DB_PASSWORD=password -e DB_IP=host.docker.internal \
    fia-auth:local

Then visit http://127.0.0.1:8000/docs

Note: refresh_token cookies are set with Secure and SameSite=Lax. When testing via a browser over http, the cookie may
not be stored. For local debugging, prefer API clients (curl/httpie) or run behind https.

## Development

- Formatting/linting: Ruff
- Tests: pytest

Install dev extras:

`pip install .[formatting,test]`


The e2e tests will create the SQLAlchemy tables automatically against your configured Postgres (see test/e2e/conftest.py).
Ensure DB_IP, DB_USERNAME, and DB_PASSWORD are set and that database `fia` exists.

## Security and configuration notes

- Change JWT_SECRET and FIA_AUTH_API_KEY in all environments; defaults are insecure and for tests only
- The /experiments endpoint is internal and protected by the API key via Authorization: Bearer
- Access tokens are short-lived; use /refresh with the HttpOnly cookie to get a new one
- The service trusts UOWS for authentication and identity data; ensure network connectivity and valid API keys

## License

GPL-3.0
