#!/usr/bin/env python3
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'email': self.email
        }


class Categories(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(Integer(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id
        }


class Items(Base):
    __tablename__ = 'items'
    __table_args__ = (UniqueConstraint('category_name', name='key'), )

    title = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_name = Column(Integer, ForeignKey('categories.name'))
    category = relationship(Categories, backref='items')
    user_id = Column(String(80), ForeignKey('users.id'))
    user = relationship(Users, backref='items')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'category_name': self.category_name
        }


engine = create_engine('sqlite:///categoriesitems.db')

Base.metadata.create_all(engine)
