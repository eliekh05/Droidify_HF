"""FastAPI application — startup, CORS, route registration, cache warm."""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.devices import router as devices_router
from app.api.android_versions import router as android_router
from app.api.tools import router as tools_router
from app.api.roms import router as roms_router
from app.api.recoveries import router as recoveries_router
from app.api.guides import router as guides_router
from app.api.auth import router as auth_router
from app.api.terms_api import router as terms_router

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# In the HF container: WORKDIR is /home/user/app
# frontend/ is copied to /home/user/app/frontend/
# Use env var for flexibility, fall back to absolute container path
import os as _os
STATIC_DIR = Path(_os.environ.get("STATIC_DIR", "/home/user/app/frontend"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    _log = logging.getLogger("droidify.startup")
    from app.services.cache import load_from_disk, save_to_disk
    from app.db import init_db
    await init_db()
    restored = load_from_disk()
    _log.warning("Cache restored: %d entries from disk", restored)
    _log.warning("Warming caches...")

    async def _warm():
        try:
            from app.scrapers.devices import _get_all_devices
            from app.scrapers.recoveries import get_recoveries
            from app.scrapers.android_versions import get_android_versions
            from app.scrapers.tools import get_tools
            await asyncio.gather(
                _get_all_devices(),
                get_android_versions(),
                get_tools(),
                return_exceptions=True,
            )
            _log.warning("Phase 1 warm complete")

            from app.scrapers.sourceforge_roms import get_sourceforge_roms
            from app.scrapers.pixelexperience import get_pixelexperience_roms
            from app.scrapers.community_roms import get_all_community_roms
            from app.scrapers.gsi_roms import get_gsi_roms
            await asyncio.gather(
                get_sourceforge_roms(),
                get_pixelexperience_roms(),
                get_all_community_roms(),
                get_gsi_roms(),
                get_recoveries(limit=1),
                return_exceptions=True,
            )
            _log.warning("Phase 2 warm complete")

            from app.scrapers.roms import _build_lookup
            from app.scrapers.unofficialtwrp import get_unofficialtwrp_devices
            await asyncio.gather(
                get_unofficialtwrp_devices(),
                _build_lookup(),
                return_exceptions=True,
            )
            _log.warning("Phase 3 warm complete — all caches hot")
        except Exception as e:
            _log.error("Warmup error: %s", e)

    asyncio.get_event_loop().create_task(_warm())
    yield
    save_to_disk()
    _log.warning("Cache saved to disk on shutdown")

app = FastAPI(
    title="Droidify API",
    description="Live Android ROM, device and recovery indexer. No auth required. All endpoints are GET-only.",
    version="2.0.0",
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# API routes — all under /api/
app.include_router(devices_router,      prefix="/api/devices",          tags=["devices"])
app.include_router(roms_router,         prefix="/api/roms",              tags=["roms"])
app.include_router(recoveries_router,   prefix="/api/recoveries",        tags=["recoveries"])
app.include_router(tools_router,        prefix="/api/tools",             tags=["tools"])
app.include_router(android_router,      prefix="/api/android-versions",  tags=["android"])
app.include_router(guides_router,       prefix="/api/guides",            tags=["guides"])

@app.get("/api-reference", include_in_schema=False)
async def api_reference():
    """Human-readable styled API reference page."""
    import pathlib as _pl2
    from fastapi.responses import FileResponse as _FR2
    _static = _pl2.Path(
        os.environ.get("STATIC_DIR",
            str(_pl2.Path(__file__).parent.parent.parent / "frontend"))
    )
    return _FR2(str(_static / "openapi.html"))

@app.get("/docs", include_in_schema=False)
async def custom_docs():
    """Serve our custom styled Swagger UI."""
    return FileResponse(str(STATIC_DIR / "docs.html"))

# Reject bodies over 64KB — this is a read-only API, no large payloads expected
@app.middleware("http")
async def limit_body_size(request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > 65536:
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Request too large"}, status_code=413)
    return await call_next(request)

@app.get("/api/health")
async def health():
    return {"status": "ok", "build": "huggingface"}

# Catch-all SPA fallback — serves index.html for any path not matched above
# Must be LAST route, BEFORE the StaticFiles mount
# Handles client-side routing (e.g. /devices → index.html handles it in JS)
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    # Try exact file match
    target = STATIC_DIR / full_path
    if target.is_file():
        return FileResponse(str(target))
    # Always fall back to index.html for SPA routing
    return FileResponse(str(STATIC_DIR / "index.html"))

# Mount static files for direct asset serving (CSS, JS, images, etc.)
# Must come AFTER the catch-all route so /api/* routes and the catch-all win
if STATIC_DIR.exists():
    app.mount("/static-assets", StaticFiles(directory=str(STATIC_DIR)), name="static")
