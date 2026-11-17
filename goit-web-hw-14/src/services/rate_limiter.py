import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, status

from src.conf.config import config
from src.entity.models import User
from src.services.auth import auth_service


class RateLimiter:
    """FastAPI dependency that limits repeated requests with Redis."""

    def __init__(self, times: int = 5, seconds: int = 60):
        """Configure the maximum number of requests for a time window.

        :param times: Allowed number of requests during the window.
        :type times: int
        :param seconds: Window length in seconds.
        :type seconds: int
        """
        self.times = times
        self.seconds = seconds
        self.cache = redis.Redis(
            host=config.REDIS_DOMAIN,
            port=config.REDIS_PORT,
            db=0,
            password=config.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True,
        )

    async def __call__(
        self,
        request: Request,
        user: User = Depends(auth_service.get_current_user),
    ):
        """Check and increment the request counter for the current user.

        :param request: The incoming FastAPI request.
        :type request: Request
        :param user: The authenticated user.
        :type user: User
        :raises HTTPException: If the request limit has been exceeded.
        """
        key = f"rate_limit:{user.id}:{request.method}:{request.url.path}"
        requests_count = await self.cache.incr(key)

        if requests_count == 1:
            await self.cache.expire(key, self.seconds)

        if requests_count > self.times:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too Many Requests",
            )
