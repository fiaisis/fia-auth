from starlette.requests import Request
from starlette.responses import JSONResponse


async def auth_error_handler(_: Request, __: Exception) -> JSONResponse:
    """
    Automatically return a 403 when an authentication error is raised
    :param _:
    :param __:
    :return: JSONResponse with 404
    """
    return JSONResponse(
        status_code=403,
        content={"message": "Forbidden"},
    )
