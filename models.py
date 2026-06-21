from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class Survey(Base):
    __tablename__ = "surveys"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String)
    question = Column(String)
    slug = Column(String, unique=True, index=True)


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    survey_id = Column(Integer, ForeignKey("surveys.id"))
    answer = Column(String)