from fastapi import Request, HTTPException, status
from ..utils.rate_limiter import RateLimiter
from ..config import settings

rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_max_requests,
    time_window=settings.rate_limit_time_window,
)


async def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host


async def check_rate_limit(request: Request):
    client_ip = await get_client_ip(request)
    if not await rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试",
        )