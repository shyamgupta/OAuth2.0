# SQLAlchemy - Configuration Code
import sys 
from sqlalchemy import Column, ForeignKey,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()

# Class, Table, Mapper Code
class User(Base):
    __tablename__ = 'user'
    name = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False,unique=True)
    id = Column(Integer, primary_key = True)


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80),nullable=False)
    id = Column(Integer,primary_key=True)
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Item(Base):
    __tablename__ = 'item'
    name = Column(String(80))
    description = Column(String(5000))
    id = Column(Integer,primary_key=True)
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description':self.description,
            'category_id':self.category_id
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)