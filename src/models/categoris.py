from sqlalchemy import Column, Integer, String
from src.models import Base

class Categoris(Base): 
    __tablename__ = 'categoris'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False) 
    description = Column(String(200), nullable=True)


    def __init__(self, name, description = None): 
        self.name = name
        self.description = description

    def __repr__(self):
       return f"<Category(id={self.id}, name='{self.name}', description='{self.description}')>"     