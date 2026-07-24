from sqlalchemy import create_engine  
from sqlalchemy.orm import DeclarativeBase



engine = create_engine(url="sqlite:///./tasks.db", echo=True, connect_args={"check_same_thread":False})


class Base(DeclarativeBase):
    pass 

