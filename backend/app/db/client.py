"""Single shared Supabase client instance used by both the API and the pipeline."""

from supabase import Client, create_client

from app.config import settings


def get_supabase_client() -> Client:
    return create_client(settings.supabase_url, settings.supabase_key)


supabase = get_supabase_client()
