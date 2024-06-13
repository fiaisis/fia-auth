# fia-auth
[![codecov](https://codecov.io/gh/fiaisis/fia-auth/graph/badge.svg?token=lzm0DS1jhG)](https://codecov.io/gh/fiaisis/fia-auth)
![License: GPL-3.0](https://img.shields.io/github/license/fiaisis/run-detection)
![Build: passing](https://img.shields.io/github/actions/workflow/status/fiaisis/fia-auth/tests.yml?branch=main)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-30173d)](https://docs.astral.sh/ruff/)
[![linting: ruff](https://img.shields.io/badge/linting-ruff-30173d)](https://docs.astral.sh/ruff/)

## Testing Locally
You must be connected to the vpn to make use of the uows and allocations api.

You must set the following Env vars:

- UOWS_API_KEY

Additional env vars are optional for local testing:
- ALLOCATIONS_URL - defaults to dev allocations
- API_KEY - defaults to `"shh"` - This is the internal API key for the experiments endpoint

