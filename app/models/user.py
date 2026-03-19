from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.core.logger import logger
class User(Base):
    __tablename__ = 'users'
 
    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    username        = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active       = Column(Boolean, default=True)
    role            = Column(String, default='user')  
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    notes = relationship('Note', back_populates='owner', cascade='all, delete-orphan')
    logger.debug("User model initialized")

