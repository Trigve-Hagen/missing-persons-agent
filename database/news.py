# schema - news - newsId, station, article, URL
# what could be used to grab the text of the article?
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR, DateTime, Boolean, func
from base import Base # Import shared base

class News(Base):
  def __init__(self):
    pass
