# fia-auth
[![codecov](https://codecov.io/gh/fiaisis/fia-auth/graph/badge.svg?token=lzm0DS1jhG)](https://codecov.io/gh/fiaisis/fia-auth)
![License: GPL-3.0](https://img.shields.io/github/license/fiaisis/fia-auth)
![Build: passing](https://img.shields.io/github/actions/workflow/status/fiaisis/fia-auth/tests.yml?branch=main)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-30173d)](https://docs.astral.sh/ruff/)
[![linting: ruff](https://img.shields.io/badge/linting-ruff-30173d)](https://docs.astral.sh/ruff/)

## Testing Locally
You must be connected to the vpn to make use of the uows and allocations api.

You must set the following Env vars:

- UOWS_API_KEY - The user office web service API Key
- FIA_AUTH_API_KEY - The API key value fia-api needs to provide for experiment number endpoint
- DB_USERNAME - DB Username
- DB_PASSWORD - DB Password
- DB_IP - IP or host of the database
- PRIVATE_KEY - The secret value used to sign JWTs

Additional env vars are optional for local testing:
- ALLOCATIONS_URL - defaults to dev allocations
- UOWS_URL - The url of the user office web service
- ACCESS_TOKEN_LIFETIME_MINUTES - the lifetime of access tokens in minutes, defaults to 10
