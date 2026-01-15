from typing import Callable
from fastapi import Depends, HTTPException, status

from app.core.auth import get_current_user
from app.models.enums import UserRole
from app.models.user import User

def require_roles(*allowed: UserRole) -> Callable:
    allowed_set = {r.value for r in allowed}

    def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role.value not in allowed_set:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _dep

require_agent = require_roles(UserRole.agent, UserRole.admin)
require_admin = require_roles(UserRole.admin)
