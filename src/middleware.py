import time
import uuid
import asyncio
from typing import Callable, Dict, Tuple
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from app.logging_config import get_logger
from app.config import settings

logger = get_logger(__name__)

from starlette.middleware.base import BaseHTTPMiddleware

class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for request tracking and performance monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            # Add request ID to response headers
            response.headers["x-request-id"] = request_id
            return response
        finally:
            # Log request completion
            duration = time.time() - start_time
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "duration_ms": round(duration * 1000, 2)
                }
            )

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global error handler for production with proper exception handling"""
    
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Handle custom API exceptions
    from app.exceptions import BaseAPIException
    if isinstance(exc, BaseAPIException):
        logger.warning(
            f"API exception: {exc.detail}",
            extra={
                "request_id": request_id,
                "status_code": exc.status_code,
                "error_code": exc.error_code
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "error_code": exc.error_code,
                "request_id": request_id,
                "status_code": exc.status_code
            },
            headers=exc.headers
        )
    
    # Handle standard HTTP exceptions
    if isinstance(exc, HTTPException):
        logger.warning(
            f"HTTP exception: {exc.detail}",
            extra={"request_id": request_id, "status_code": exc.status_code}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "request_id": request_id,
                "status_code": exc.status_code
            },
            headers=exc.headers
        )
    
    # Log unexpected errors (don't expose details in production)
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True
    )
    
    # Don't expose internal error details in production
    error_message = "Internal server error"
    if settings.is_development:
        error_message = f"Internal server error: {str(exc)}"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": error_message,
            "request_id": request_id,
            "status_code": 500
        }
    )

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting application metrics with thread-safe operations"""
    
    def __init__(self, app):
        super().__init__(app)
        self.metrics_store = _metrics_store  # Use global metrics store
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        await self.metrics_store.increment_request()
        
        try:
            response = await call_next(request)
            
            # Track response time
            duration = time.time() - start_time
            await self.metrics_store.add_response_time(duration)
            
            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            await self.metrics_store.increment_error()
            raise e

# Global metrics store - shared across all middleware instances
class MetricsStore:
    """Thread-safe metrics store"""
    def __init__(self):
        self._request_count = 0
        self._error_count = 0
        self._response_times = deque(maxlen=1000)
        self._lock = asyncio.Lock()
    
    async def increment_request(self):
        async with self._lock:
            self._request_count += 1
    
    async def increment_error(self):
        async with self._lock:
            self._error_count += 1
    
    async def add_response_time(self, duration: float):
        async with self._lock:
            self._response_times.append(duration)
    
    def get_metrics(self) -> dict:
        """Get current metrics (called from sync context)"""
        response_times = list(self._response_times)
        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times else 0
        )
        
        # Calculate percentiles
        sorted_times = sorted(response_times) if response_times else []
        p95 = sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0
        p99 = sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0
        
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._request_count, 1),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "p95_response_time_ms": round(p95 * 1000, 2),
            "p99_response_time_ms": round(p99 * 1000, 2),
            "recent_requests": len(response_times)
        }

# Global metrics store instance
_metrics_store = MetricsStore()

def get_metrics_data():
    """Get metrics from the global store"""
    return _metrics_store.get_metrics()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Production-grade rate limiting middleware using sliding window algorithm.
    Tracks requests per IP address.
    """
    
    def __init__(self, app, requests_per_minute: int = None, window_seconds: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
        # Store request timestamps per client (IP address)
        self._client_requests: Dict[str, deque] = defaultdict(lambda: deque())
        self._cleanup_interval = 300  # Clean up old entries every 5 minutes
        self._last_cleanup = time.time()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded IP (when behind proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _cleanup_old_entries(self):
        """Remove old entries to prevent memory leaks"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff_time = current_time - self.window_seconds
        clients_to_remove = []
        
        for client_ip, timestamps in self._client_requests.items():
            # Remove timestamps outside the window
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            
            # Remove empty entries
            if not timestamps:
                clients_to_remove.append(client_ip)
        
        for client_ip in clients_to_remove:
            del self._client_requests[client_ip]
        
        self._last_cleanup = current_time
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/health", "/health/detailed", "/metrics"]:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Cleanup old entries periodically
        self._cleanup_old_entries()
        
        # Get or create request queue for this client
        client_queue = self._client_requests[client_ip]
        
        # Remove requests outside the time window
        cutoff_time = current_time - self.window_seconds
        while client_queue and client_queue[0] < cutoff_time:
            client_queue.popleft()
        
        # Check if rate limit exceeded
        if len(client_queue) >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={"client_ip": client_ip, "path": request.url.path}
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_minute} per {self.window_seconds} seconds",
                    "retry_after": self.window_seconds
                },
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": str(max(0, self.requests_per_minute - len(client_queue))),
                    "X-RateLimit-Reset": str(int(current_time + self.window_seconds))
                }
            )
        
        # Add current request timestamp
        client_queue.append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining = max(0, self.requests_per_minute - len(client_queue))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response