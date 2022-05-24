import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
import os


Base = declarative_base()
db_login = os.getenv('db_login')
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')


db = f'postgresql://{db_login}:{db_password}@localhost:5432/{db_name}'
engine = sq.create_engine(db)
Session = sessionmaker(bind=engine)
session = Session()


class SearchParams(Base):

    __tablename__ = 'searching_parameters'

    id = sq.Column(sq.Integer, unique=True, autoincrement=True)
    user_id = sq.Column(sq.Integer, primary_key=True)
    search_parameters = sq.Column(sq.Text, primary_key=True)


class FoundedUsers(Base):

    __tablename__ = 'founded_users'

    searching_parameters_id = sq.Column(sq.Integer,
                                        sq.ForeignKey('searching_parameters.id'),
                                        primary_key=True
                                        )
    user_id = sq.Column(sq.Integer, primary_key=True)
    user_photos = sq.Column(sq.Text)


class City(Base):

    __tablename__ = 'cities'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    name = sq.Column(sq.String)



# q = session.query(City).where(City.name == '').first()
# print(q)