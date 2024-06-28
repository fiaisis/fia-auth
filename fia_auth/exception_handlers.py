import logging
from http import HTTPStatus

from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


async def auth_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """
    Automatically return a 403 when an authentication error is raised
    :param _:
    :param exc: The caught exception
    :return: JSONResponse with 403
    """
    logger.info(f"Exception was caught {exc}")
    return JSONResponse(
        status_code=HTTPStatus.FORBIDDEN,
        content={"message": "Forbidden"},
    )
