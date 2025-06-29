from sqlalchemy import Column, String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from emby_recommendation_engine.shared.database import Base
import uuid


class User(Base):  # Remove @define decorator
    """Users from Emby server."""

    __tablename__ = "users"  # Remove ClassVar typing

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    emby_user_id = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<User(emby_id='{self.emby_user_id}', username='{self.username}')>"
