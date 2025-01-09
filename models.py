from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()
engine = create_engine(
    "sqlite:///sqlite.db",
    connect_args={"check_same_thread": False},
)

"""

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    # One-to-one relationship with child (one parent has one child)
    child = relationship('Child', back_populates='parent', uselist=False)
    
    def __str__(self):
        return self.name


class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('parent.id'), nullable=False, unique=True)
    
    # One-to-one relationship with parent (one child has one parent)
    parent = relationship(Parent, back_populates='child')
    
    def __str__(self):
        return self.name

"""


## use backref function

class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    def __str__(self):
        return self.name


class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('parent.id'), nullable=False, unique=True)
    
    # parent relation
    parent = relationship(Parent, backref=backref('child', uselist=False))
    
    def __str__(self):
        return self.name


Base.metadata.create_all(engine)  # Create tables