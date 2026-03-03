from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes.export import router as export_router
from api.routes.generate import router as generate_router

app = FastAPI(
    title="Smart Timetable Scheduler",
    description="Timetable scheduling via graph coloring and genetic algorithms",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router, prefix="/api", tags=["scheduler"])
app.include_router(export_router, prefix="/api", tags=["export"])


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


# serve built frontend if available
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
