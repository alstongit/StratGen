from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from config.supabase_client import get_admin_supabase_client

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Verify JWT token and return user data.
    """
    try:
        token = credentials.credentials
        
        # Get Supabase client
        supabase = get_admin_supabase_client()
        
        # Verify token and get user
        user_response = supabase.auth.get_user(token)
        
        # Check if user exists
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        user = user_response.user
        
        # Extract user ID - Supabase returns it as user.id
        user_id = user.id
        user_email = user.email if hasattr(user, 'email') else None
        
        print(f"✅ User authenticated: {user_email} (ID: {user_id})")
        
        # Return standardized format with 'sub' field
        return {
            "sub": user_id,
            "id": user_id,
            "email": user_email
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Auth error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )