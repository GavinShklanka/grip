"""GRIP FastAPI Application Shell."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.db.session import init_db
from backend.api import state, topology, scenario, forecast, meta

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    engine = init_db(); from backend.db.session import create_tables; create_tables(engine)

    if settings.demo_mode:
        logger.info("Starting GRIP in DEMO_MODE — seeding data...")
        from backend.db.session import get_session_factory
        from backend.db.demo_seed import seed_demo_data
        Session = get_session_factory()
        db = Session()
        try:
            print("GRIP: Seeding demo database — this takes ~4 minutes on first run...")
            seed_demo_data(db)
            print("GRIP: Demo seed complete. Server ready.")
        finally:
            db.close()

    yield


app = FastAPI(
    title="GRIP API",
    description="Geopolitical Resilience Intelligence Platform Core Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(state.router, prefix="/api/state", tags=["State"])
app.include_router(topology.router, prefix="/api/topology", tags=["Topology"])
app.include_router(scenario.router, prefix="/api/scenario", tags=["Scenario"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(meta.router, prefix="/api/meta", tags=["Metadata"])

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "online", "mode": "demo" if get_settings().demo_mode else "live"}

# Serve frontend static files in production
from pathlib import Path
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    # Serve assets
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

    # SPA catch-all: serve index.html for all non-API routes
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIST / "index.html"))

