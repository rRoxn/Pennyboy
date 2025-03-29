from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True)
    balance = Column(Integer, default=0, nullable=False)
    last_daily = Column(DateTime, nullable=True)
    total_earned = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, balance={self.balance})>" 