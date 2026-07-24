import json
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from core.limiter import limiter
from core.db import Base, engine
from routers.auth import router as auth_router
from routers.tasks import router as tasks_router
from security_check.sql_inject import router as sqli_router

load_dotenv(override=True)

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

@asynccontextmanager
async def lifespan( app: FastAPI ):
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	yield

app = FastAPI(lifespan=lifespan)

if ALLOWED_HOSTS:
	app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

app.add_middleware(
	CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=True,
	allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], allow_headers=["*"], )


@app.middleware("http")
async def extract_username( request: Request, call_next ):
	if request.method == "POST" and request.url.path.endswith("/token/"):
		try:
			content_type = request.headers.get("content-type", "")
			if "application/json" in content_type:
				body = await request.body()
				if body:
					data = json.loads(body)
					request.state.username = data.get("username", "unknown")
			elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
				form = await request.form()
				request.state.username = form.get("username", "unknown")
		except Exception:
			request.state.username = "unknown"
	response = await call_next(request)
	return response

@app.middleware("http")
async def add_security_headers( request: Request, call_next ):
	response = await call_next(request)
	response.headers["Content-Security-Policy"] = ("default-src 'self'; "
	                                               "script-src 'self'; "
	                                               "style-src 'self' 'unsafe-inline'; "
	                                               "img-src 'self' data:;")
	response.headers["X-Content-Type-Options"] = "nosniff"
	response.headers["X-Frame-Options"] = "DENY"
	response.headers["X-XSS-Protection"] = "1; mode=block"
	
	if not DEBUG:
		response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
	
	return response


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(tasks_router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(sqli_router, prefix="/api/security-test", tags=["Test"])


@app.get("/")
def root():
	return {"message": "FastAPI работает!"}
