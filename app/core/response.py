from fastapi.responses import JSONResponse


def ok(data=None):
    return {"code": 0, "message": "ok", "data": data if data is not None else {}}


def paginated(items, page, page_size, total):
    return ok({"items": items, "page": page, "page_size": page_size, "total": total})


def error(code: int, message: str, data=None, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "message": message, "data": data or {}},
    )
