from sqlalchemy import Column, Integer, String
from src.models import Base,session

class Categoris(Base): 
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False) 
    description = Column(String(200), nullable=True)


    def __init__(self, name, description = None): 
        self.name = name
        self.description = description
    @staticmethod
    def get_by_id(category_id):
        return session.query(Categoris).filter_by(id=category_id).first()
   