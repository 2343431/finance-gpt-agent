from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    preferences = relationship("UserPreferences", back_populates="user")

class UserPreferences(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'))
    preference_key = Column(String(50))
    preference_value = Column(String(100))
    user = relationship("UserProfile", back_populates="preferences")

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_profiles.id'))
    conversation_history = Column(String)
    user = relationship("UserProfile")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"