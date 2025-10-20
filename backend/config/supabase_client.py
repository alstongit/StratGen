from supabase import create_client, Client
from config.settings import settings

# Admin client - Full access (bypasses RLS)
# Use this for system operations that need full database access
supabase_admin: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_KEY
)

def get_user_supabase_client(user_token: str) -> Client:
    """
    Creates a Supabase client with user's JWT token.
    This client respects RLS policies just like the frontend.
    
    Args:
        user_token: User's JWT access token
    
    Returns:
        Supabase client instance scoped to the user
    """
    client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )
    
    # Set the auth token for this client
    client.postgrest.auth(user_token)
    
    return client

def get_admin_supabase_client() -> Client:
    """
    Returns the admin Supabase client.
    Use with caution - this bypasses all RLS policies.
    
    Returns:
        Supabase admin client
    """
    return supabase_admin