class StatusCode:
    # 웹 사이트 서버에 문제가 있음을 의미하지만 서버는 정확한 문제에 대해 더 구체적으로 설명할 수 없습니다.
    HTTP_500 = 500
    # 요청이 성공적이었으며 그 결과로 새로운 리소스가 생성
    HTTP_201 = 201
    # 요청이 성공적으로 되었습니다. 성공의 의미는 HTTP 메서드에 따라 달라진다.
    HTTP_200 = 200


class APIException(Exception):
    status_code: int
    code: str
    message: str
    detail: str

    def __init__(
        self,
        *,
        status_code: int = StatusCode.HTTP_500,
        message: str = None,
        detail: str = None,
        ex: Exception = None,
    ):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(ex)


class SuccessException(APIException):
    def __init__(self, detail_msg: str = None, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_200,
            message="요청에 성공하였습니다.",
            detail=f"Success : {detail_msg}",
            ex=ex,
        )


class FailException(APIException):
    def __init__(self, detail_msg: str = None, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_500,
            message="요청에 실패하였습니다.",
            detail=f"Fail : {detail_msg}",
            ex=ex,
        )
