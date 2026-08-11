from fastapi import APIRouter, Header, HTTPException
from app.config import settings
from app.pipeline.run import run_pipeline
from app.pipeline.send_daily_digest import send_all_digests

router = APIRouter(prefix="/api/cron", tags=["cron"])

def verify_cron_secret(authorization: str = Header(None)):
    """Vercel Cron Jobs can be configured to send a secret in the Authorization
    header, so we can verify the request genuinely came from Vercel's scheduler
    and not from a random public request to this URL.
    """
    expected = f"Bearer {settings.cron_secret}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

@router.get("/run-pipeline")
def trigger_pipeline(authorization: str = Header(None)):
    verify_cron_secret(authorization)
    run_pipeline()
    return {"status": "pipeline run complete"}

@router.get("/send-digest")
def trigger_digest(authorization: str = Header(None)):
    verify_cron_secret(authorization)
    send_all_digests()
    return {"status": "digest run complete"}
