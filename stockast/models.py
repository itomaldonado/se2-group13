from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

# base declarative class for SQLAlchemy
Base = declarative_base()


class Company(Base):
    """Class representing the 'companies' table"""
    __tablename__ = 'companies'

    symbol = Column(String(50), nullable=False, primary_key=True)
    name = Column(String(250), nullable=False)
    exchange = Column(String(50), nullable=False)


class StockHistory(Base):
    """Class representing the 'stocks_history' table"""
    __tablename__ = 'stocks_history'

    symbol = Column(ForeignKey('companies.symbol'), index=True, primary_key=True)
    date = Column(Date, index=True, primary_key=True)
    day_open = Column(Float, nullable=False)
    day_close = Column(Float, nullable=False)
    day_high = Column(Float, nullable=False)
    day_low = Column(Float, nullable=False)
    day_volume = Column(Integer, nullable=False)


class StockRealTime(Base):
    """Class representing the 'stocks_real_time' table"""
    __tablename__ = 'stocks_real_time'

    symbol = Column(ForeignKey('companies.symbol'), index=True, primary_key=True)
    timestamp = Column(TIMESTAMP, index=True, primary_key=True)
    price = Column(Float, nullable=False)
