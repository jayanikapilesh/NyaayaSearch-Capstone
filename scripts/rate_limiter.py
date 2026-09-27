import time
from collections import defaultdict
from fastapi import Request, HTTPException

RATE_LIMIT_REQUESTS = 20
RATE_LIMIT_WINDOW_SECONDS = 600  # 10 minutes

_ip_timestamps: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT_MESSAGES = {
    "en": "Too many requests. Please wait a few minutes before trying again (limit: 20 requests per 10 minutes).",
    "hi": "बहुत अधिक अनुरोध। कृपया कुछ मिनट बाद पुनः प्रयास करें (सीमा: 10 मिनट में 20 अनुरोध)।",
    "kn": "ಹೆಚ್ಚಿನ ವಿನಂತಿಗಳು ಬಂದಿವೆ. ದಯವಿಟ್ಟು ಕೆಲವು ನಿಮಿಷಗಳ ನಂತರ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ (ಮಿತಿ: 10 ನಿಮಿಷಗಳಲ್ಲಿ 20 ವಿನಂತಿಗಳು).",
}


def get_client_ip(request: Request) -> str:
    """Extract client IP, taking into account reverse proxies (X-Forwarded-For / X-Real-IP)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


def check_rate_limit(request: Request, language: str = "en") -> None:
    """Checks and records a request for the client IP.
    Raises HTTPException(429) if the client has exceeded RATE_LIMIT_REQUESTS within RATE_LIMIT_WINDOW_SECONDS.
    """
    ip = get_client_ip(request)
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS

    history = [t for t in _ip_timestamps[ip] if t > cutoff]
    if len(history) >= RATE_LIMIT_REQUESTS:
        _ip_timestamps[ip] = history
        lang = language if language in RATE_LIMIT_MESSAGES else "en"
        msg = RATE_LIMIT_MESSAGES[lang]
        raise HTTPException(status_code=429, detail=msg)

    history.append(now)
    _ip_timestamps[ip] = history


def reset_rate_limits() -> None:
    """Reset all stored timestamps (primarily for unit tests)."""
    _ip_timestamps.clear()
