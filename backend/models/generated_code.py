from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.core.database import Base

class GeneratedCode(Base):
    __tablename__ = "generated_codes"
    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(Text, nullable=False)
    language = Column(String, nullable=True)
    agent_name = Column(String, nullable=True)
    version = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    requirement = relationship("Requirement", back_populates="codes")
    user = relationship("User", back_populates="generated_codes") 