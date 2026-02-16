from app.core.config import settings
from app.db.game_store import store as in_memory_store
from app.db.supabase_store import store as supabase_store

# Use Supabase store in production/staging, in-memory for local development
if settings.environment in ("production", "staging"):
    store = supabase_store
else:
    store = in_memory_store
