from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, func
from datetime import datetime
from src.models import Base, session

class Invoices(Base):
    __tablename__='invoices'
    id=Column(Integer, primary_key=True)
    client_id=Column(Integer, ForeignKey('clients.id'), nullable=False)
    user_id=Column(Integer, ForeignKey('users.id'), nullable=False)
    date=Column(DateTime, nullable=False, default=datetime.now)
    total=Column(Float, default=0)
    completed=Column(Boolean, default=False)
    active=Column(Integer, default=1)
    def __init__(self, client_id, user_id):
        self.client_id=client_id; self.user_id=user_id; self.date=datetime.now()
        self.total=0; self.completed=False; self.active=1
    @staticmethod
    def get_paginated(page, per_page):
        total=session.query(func.count(Invoices.id)).scalar()
        return session.query(Invoices).offset((page-1)*per_page).limit(per_page).all(), total
    @staticmethod
    def get_by_id(invoice_id): return session.query(Invoices).filter_by(id=invoice_id).first()
    def save(self): session.add(self); session.commit()
    def update(self): session.commit()