from app.core.config import settings
from app.db.game_store import store as in_memory_store
from app.db.supabase_store import store as supabase_store

# Use Supabase store in production/staging, or if specifically requested
# For now, let's default to Supabase for persistence as it's the core architecture
store = in_memory_store
