# fia-auth
[![codecov](https://codecov.io/gh/fiaisis/fia-auth/graph/badge.svg?token=lzm0DS1jhG)](https://codecov.io/gh/fiaisis/fia-auth)

## Testing Locally
You must be connected to the vpn to make use of the uows and allocations api.

You must set the following Env vars:

- UOWS_API_KEY

Additional env vars are optional for local testing:
- ALLOCATIONS_URL - defaults to dev allocations
- API_KEY - defaults to `"shh"` - This is the internal API key for the experiments endpoint

