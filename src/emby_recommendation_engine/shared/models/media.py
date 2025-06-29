from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, func, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from emby_recommendation_engine.shared.database import Base
import uuid


class MediaItem(Base):  # Remove @define decorator
    """Media items from Emby with external metadata mapping."""

    __tablename__ = "media_items"  # Remove ClassVar typing

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    emby_item_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    type = Column(
        String(50), nullable=False, index=True
    )  # Movie, Episode, Series, etc.

    # External service IDs for data integration
    tmdb_id = Column(Integer, nullable=True, index=True)

    # Basic metadata
    production_year = Column(Integer, nullable=True, index=True)
    runtime_minutes = Column(Integer, nullable=True)
    genres = Column(ARRAY(Text), nullable=True)  # ['Action', 'Comedy', 'Drama']
    overview = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_media_items_type_year", "type", "production_year"),
        Index(
            "idx_media_items_genres", "genres", postgresql_using="gin"
        ),  # For array searches
    )

    def __repr__(self):
        return f"<MediaItem(emby_id='{self.emby_item_id}', name='{self.name}', type='{self.type}')>"
