from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from stockast.models import Base
from stockast.models import Company

# databse Engine
engine = create_engine('sqlite:///test.db', echo=True)

# create all tables if needed
Base.metadata.create_all(engine)

# create session
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

# create a new company
apple = Company(name='Apple Inc.', exchange='NASDAQ', symbol='AAPL')

# add the company to the database/session
session.add(apple)

# commit all changes to the database
session.commit()

# show that now the company has an ID given by the database
print(f'Apple company id: {apple.symbol}')

# close the session
session.close()
