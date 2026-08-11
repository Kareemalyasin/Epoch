"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.articles import router as articles_router
from app.api.routes.cron import router as cron_router
from app.api.routes.subscribers import router as subscribers_router

app = FastAPI(title="AI News Aggregator")

# Allow the local Vite dev server to call this API from the browser (Vite
# picks the next free port (5173, 5174, ...) if one is already in use, so a
# couple of likely dev ports are listed here rather than just one), plus the
# deployed Vercel frontend. Vercel generates a new random preview URL per
# deployment (e.g. epoch-o5o7orx2j-epoch6.vercel.app), so allow_origin_regex
# covers any *.vercel.app subdomain rather than just the production domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://epoch-gold-sigma.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles_router)
app.include_router(subscribers_router)
app.include_router(cron_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
