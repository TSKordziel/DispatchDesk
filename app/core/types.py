from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.auth import get_current_user
from app.core.rbac import require_agent
from app.models.user import User

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AgentUser = Annotated[User, Depends(require_agent)]
