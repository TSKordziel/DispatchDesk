from fastapi import HTTPException

STATUS_CODE_TO_ERROR_CODE = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "unprocessable",
    500: "internal_error",
}


def build_error(*, code: str, message: str, details, request_id: str | None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "request_id": request_id,
        }
    }


def raise_http_error(
    status_code: int,
    message: str,
    *,
    code: str | None = None,
    details=None,
) -> None:
    resolved_code = code or STATUS_CODE_TO_ERROR_CODE.get(status_code, "error")
    raise HTTPException(
        status_code=status_code,
        detail={
            "code": resolved_code,
            "message": message,
            "details": details,
        },
    )


def bad_request(message: str = "Bad request", *, details=None) -> None:
    raise_http_error(400, message, details=details)


def unauthorized(message: str = "Unauthorized", *, details=None) -> None:
    raise_http_error(401, message, details=details)


def forbidden(message: str = "Forbidden", *, details=None) -> None:
    raise_http_error(403, message, details=details)


def not_found(resource: str = "Resource") -> None:
    raise_http_error(404, f"{resource} not found")


def conflict(message: str = "Conflict", *, details=None) -> None:
    raise_http_error(409, message, details=details)


def unprocessable(message: str = "Unprocessable entity", *, details=None) -> None:
    raise_http_error(422, message, details=details)
