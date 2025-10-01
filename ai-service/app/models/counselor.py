"""
Counselor model - Professional counselors
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship

from app.models import Base


class Counselor(Base):
    """
    Counselor profile - professionals who can view all student data
    """
    __tablename__ = "counselors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Professional info
    license_number = Column(String(100), unique=True, nullable=True)  # Số chứng chỉ hành nghề
    specialization = Column(String(255), nullable=True)  # Chuyên môn
    years_of_experience = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)
    
    # Contact
    phone_number = Column(String(20), nullable=True)
    office_location = Column(String(255), nullable=True)
    
    # Status
    is_available = Column(Boolean, default=True)  # Có sẵn sàng tư vấn không

    # Relationships
    user = relationship("User", back_populates="counselor")

    def __repr__(self):
        return f"<Counselor(id={self.id}, license={self.license_number})>"
