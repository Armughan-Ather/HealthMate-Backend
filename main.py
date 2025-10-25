import routes
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from tasks.scheduler import start_scheduler
import os
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

is_production = os.getenv("ENV") == "production"

app = FastAPI(
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve favicon
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

# Serve root route with logo
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>HealthMate API</title>
            <link rel="icon" href="/favicon.ico" type="image/x-icon" />
        </head>
        <body style="font-family: Arial; text-align: center; padding: 40px;">
            <img src="/static/healthmate_logo.png" alt="HealthMate Logo" width="200"/>
            <h1>🚀 HealthMate API</h1>
            <p>Your wellness companion.</p>
            <p>All endpoints are secured and documentation is disabled in production.</p>
        </body>
    </html>
    """

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_origins=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)

Base.metadata.create_all(bind=engine)

app.include_router(routes.router)

# ✅ Start scheduler only when FastAPI is ready
@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})
