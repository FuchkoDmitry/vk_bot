import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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
Base.metadata.create_all(engine)


class User(Base):

    __tablename__ = 'user'

    user_id = sq.Column(sq.Integer, unique=True, primary_key=True)
    firstname = sq.Column(sq.String)
    lastname = sq.Column(sq.String)
    search_params_list = relationship('SearchParams', back_populates='user')

    @classmethod
    def check_user(cls, user_id):
        request = session.query(cls).where(
            cls.user_id == user_id
        ).first()
        if request is None:
            return False
        return request

    @classmethod
    def add_user(cls, user_id, first_name, last_name):
        new_user = User(
            user_id=user_id,
            firstname=first_name,
            lastname=last_name
        )
        session.add(new_user)
        session.commit()


class SearchParams(Base):

    __tablename__ = 'searching_parameters'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.user_id'))
    search_parameters = sq.Column(sq.Text)
    user = relationship(User)

    def add_search_params(self, user_id, params):
        request = session.query(SearchParams).where(and_(
            SearchParams.user_id == user_id,
            SearchParams.search_parameters == params)
        ).first()
        if request is None:
            self.user_id = user_id
            self.search_parameters = params
            session.add(self)
            session.commit()
            # print('параметры добавлены в бд params-->', self.search_parameters)
            return self.id
        else:
            # print('параметры были в бд' + request.search_parameters)
            return request.id


class FoundedUsersCount(Base):

    __tablename__ = 'founded_users_count'

    searching_parameters_id = sq.Column(sq.Integer,
                                        sq.ForeignKey('searching_parameters.id'),
                                        primary_key=True
                                        )
    user_id = sq.Column(sq.Integer)
    founded_users_count = sq.Column(sq.Integer)
    # user_photos = sq.Column(sq.Text)

    def check_count(self, user_id, search_params_id):
        # print('search_params_id', search_params_id)
        request = session.query(FoundedUsersCount).where(and_(
            FoundedUsersCount.user_id == user_id,
            FoundedUsersCount.searching_parameters_id == search_params_id)
        ).first()
        if request is None:
            self.user_id = user_id
            self.searching_parameters_id = search_params_id
            self.founded_users_count = 0
            session.add(self)
            session.commit()
            return self.founded_users_count
        else:
            return request.founded_users_count

    @classmethod
    def update_count(cls, search_params_id, count_to_add):
        current_count = session.query(cls).where(
            cls.searching_parameters_id == search_params_id
        ).first().founded_users_count
        session.query(cls).filter(
            cls.searching_parameters_id == search_params_id).update(
            {'founded_users_count': count_to_add + current_count}
        )
        session.commit()
        current_count = session.query(cls).where(
            cls.searching_parameters_id == search_params_id
        ).first().founded_users_count

    @classmethod
    def clear_count(cls, user_id):
        searching_params = session.query(cls).where(
            cls.user_id == user_id
        ).all()
        if searching_params:
            for searching_param in searching_params:
                searching_param.founded_users_count = 0
                session.add(searching_param)
                session.commit()
        # print(request.founded_users_count)
        # request.founded_users_count = 0
        # print(request.founded_users_count)
        # session.add(request)
        # session.commit()


class UserPhotos(Base):

    __tablename__ = 'user_photos'

    user_id = sq.Column(
        sq.Integer,
        primary_key=True
    )
    user_photos = sq.Column(sq.Text)

    @classmethod
    def check_user(cls, user_id):
        user = session.query(cls).where(
            cls.user_id == user_id
        ).first()
        if user is not None:
            return user
        return False

    @classmethod
    def add_user(cls, user_photos):
        new_user = UserPhotos(
            user_id=user_photos[0],
            user_photos=user_photos[1]
        )
        session.add(new_user)
        session.commit()
        # print('user' + str(user_photos[0]) + 'added to db with photos' + user_photos[1])


class City(Base):

    __tablename__ = 'cities'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    name = sq.Column(sq.String)


class Favorites(Base):

    __tablename__ = 'favorites'

    user_id = sq.Column(sq.Integer, primary_key=True)
    favorite_id = sq.Column(sq.Integer, primary_key=True)
    photos_list = sq.Column(sq.Text)


class BlackList(Base):

    __tablename__ = 'black_list'

    user_id = sq.Column(sq.Integer, primary_key=True)
    blacklisted_user_id = sq.Column(sq.Integer, primary_key=True)
    photos_list = sq.Column(sq.Text)



Base.metadata.create_all(engine)

# request = session.query(SearchParams).where(SearchParams.user_id==1136869).all()
# for el in request:
#     print(el.search_parameters, el.id)
#
# request = session.query(FoundedUsersCount).where(FoundedUsersCount.searching_parameters_id==7).first()
# print(request.searching_parameters_id, request.founded_users_count, request.user_id)