from sqlalchemy import Boolean, Column, DateTime, Integer, String, text
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, nullable=False, index=True)

    full_name = Column(String, nullable=False)

    password = Column(String, nullable=False)

    role = Column(String, default="user")

    is_active = Column(Boolean, default=True)

    firebase_uid = Column(String(128), nullable=True, unique=True, index=True)
    firebase_email = Column(String(255), nullable=True)
    firebase_provider = Column(String(40), nullable=True)
    firebase_linked_at = Column(DateTime, nullable=True)

    authentication_source = Column(
        String(20), nullable=False, default="local", server_default="local"
    )

    email_verified = Column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
