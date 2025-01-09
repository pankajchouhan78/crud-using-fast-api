from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()
engine = create_engine(
    "sqlite:///sqlite.db",
    connect_args={"check_same_thread": False},
)


class Parent(Base):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    
    # Explicitly define the reverse relationship in Parent
    children = relationship('Child', back_populates='parent', lazy='select')
    
    def __str__(self):
        return self.name


class Child(Base):
    __tablename__ = 'child'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('parent.id'), nullable=False)
    
    # parent relation with reverse relationship to Parent
    parent = relationship(Parent, back_populates='children', lazy='select')
    
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
    parent_id = Column(Integer, ForeignKey('parent.id'), nullable=False)
    
    # parent relation
    parent = relationship(Parent, backref=backref('children', lazy=True))
    
    def __str__(self):
        return self.name
"""

Base.metadata.create_all(engine)  # Create tables