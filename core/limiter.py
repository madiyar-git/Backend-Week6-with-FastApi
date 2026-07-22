from fastapi import Request

from slowapi import Limiter
from slowapi.util import get_remote_address

def get_ip_and_username(request: Request) -> str:
  ip = get_remote_address(request)
  username = getattr(request.state, "username", "unknown")

  return f"{ip}:{username}"

# limiter = Limiter(key_func=get_remote_address)
limiter = Limiter(key_func=get_ip_and_username)