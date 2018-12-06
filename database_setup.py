import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	username = Column(String(50), nullable=False)
	password = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)

class Blog(Base):
	__tablename__ = 'blog'

	id = Column(Integer, primary_key=True)
	titulo = Column(String(50), nullable=False)
	contenido = Column(String(250), nullable=False)
	fecha_creacion = Column(DateTime, nullable=False)
	id_autor = Column(Integer, ForeignKey("user.id"))
	user = relationship(User)

class cliente(Base):
	__tablename__ = 'cliente'
	idpedido = Column(Integer,primary_key =True)
	color = Column(String(50), nullable=False)
	medidas = Column(String(50),nullable =False)
	cantidad = Column(Integer, nullable=False)	
engine = create_engine('sqlite:///blog.db')
Base.metadata.create_all(engine)
