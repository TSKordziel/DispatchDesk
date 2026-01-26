from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import model modules so they register with Base.metadata.
# IMPORTANT: import modules, not symbols, to avoid circular imports.
import app.models.user  # noqa: F401
import app.models.ticket  # noqa: F401
import app.models.comment  # noqa: F401