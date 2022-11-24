from loguru import logger
from fastapi.responses import JSONResponse
from components.api.errors.exception import SuccessException, FailException


def FailExceptionHandler(detail_message: str, logger_message: str, code_number: int):
    response = FailException(detail_msg=detail_message)
    logger.error(logger_message)
    return JSONResponse(response.__dict__, status_code=code_number)


def SuccessExceptionHandler(detail_message: str, logger_message: str):
    response = SuccessException(detail_msg=detail_message)
    logger.error(logger_message)
    return JSONResponse(response.__dict__, status_code=200)
