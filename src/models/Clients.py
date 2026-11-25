from sqlalchemy import Column, Integer, String, func
from src.models import Base, session
import enum

class DocumentType(str, enum.Enum):
    CC='CC'; NIT='NIT'; CE='CE'

class Clients(Base):
    __tablename__='clients'
    id=Column(Integer, primary_key=True)
    document_type=Column(String(10), nullable=False)
    document_number=Column(String(20), unique=True, nullable=False)
    name=Column(String(255), nullable=False)
    email=Column(String(255), nullable=False)
    phone=Column(String(20), nullable=False)
    address=Column(String(255), nullable=False)
    active=Column(Integer, default=1)

    def __init__(self, document_type, document_number, name, email, phone, address):
        self.document_type=document_type.value if isinstance(document_type, DocumentType) else document_type
        self.document_number=document_number; self.name=name; self.email=email
        self.phone=phone; self.address=address; self.active=1

    @staticmethod
    def get_paginated(page, per_page):
        total=session.query(func.count(Clients.id)).scalar()
        return session.query(Clients).offset((page-1)*per_page).limit(per_page).all(), total
    @staticmethod
    def get_by_id(client_id): return session.query(Clients).filter_by(id=client_id).first()
    @staticmethod
    def get_by_document_number(number): return session.query(Clients).filter_by(document_number=number).first()
    def save(self): session.add(self); session.commit()
    def update(self): session.commit()