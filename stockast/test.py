from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from stockast.models import Base
from stockast.models import Company

# databse Engine
engine = create_engine('sqlite:////Users/mmaldonadofigueroa/Desktop/test.db', echo=True)

# create tables
Base.metadata.create_all(engine)

# create session
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

apple = Company(name='Apple Inc.', exchange='NASDAQ', ticker='AAPL')
session.add(apple)
session.commit()
print(f'Apple company id: {apple.id}')
session.close()
