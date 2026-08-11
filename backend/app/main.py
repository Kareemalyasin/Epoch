"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.articles import router as articles_router
from app.api.routes.subscribers import router as subscribers_router

app = FastAPI(title="AI News Aggregator")

# Allow the local Vite dev server to call this API from the browser. Vite
# picks the next free port (5173, 5174, ...) if one is already in use, so a
# couple of likely dev ports are listed here rather than just one.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles_router)
app.include_router(subscribers_router)


@app.get("/health")
def health():
    return {"status": "ok"}
