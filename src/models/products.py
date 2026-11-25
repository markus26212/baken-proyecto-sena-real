from sqlalchemy import Column, Integer, String, Float, ForeignKey, func
from src.models import Base, session


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Float, default=0)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    active = Column(Integer, default=1)  # 1 for active, 0 for inactive

    def __init__(self, name, price, category_id, description=None, stock=0):
        self.name, self.price, self.category_id = name, price, category_id
        self.description, self.stock = description, stock

    @staticmethod
    def get_paginated(page, per_page):
        total = session.query(func.count(Products.id)).scalar()
        return session.query(Products).offset((page-1)*per_page).limit(per_page).all(), total

    @staticmethod
    def get_by_id(product_id):
        return session.query(Products).filter_by(id=product_id).first()

    @staticmethod
    def get_by_name(name):
        return session.query(Products).filter_by(name=name).first()

    def save(self):
        session.add(self); session.commit()

    def update(self):
        session.commit()