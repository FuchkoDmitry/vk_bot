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
# Base.metadata.create_all(engine)


class User(Base):

    __tablename__ = 'user'

    user_id = sq.Column(sq.Integer, unique=True, primary_key=True)
    firstname = sq.Column(sq.String)
    lastname = sq.Column(sq.String)
    search_params_list = relationship('SearchParams', back_populates='user')
    favorites = relationship('UserPhotos', secondary='user_to_favorites')
    blacklisted = relationship('UserPhotos', secondary='user_to_blacklisted')

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

    @classmethod
    def add_favorite(cls, user_id, fav_user_id):
        user = cls.check_user(user_id)
        fav_user = session.query(UserPhotos).where(
            UserPhotos.user_id == fav_user_id
        ).first()
        user.favorites.append(fav_user)
        session.commit()

    @classmethod
    def add_to_blacklist(cls, user_id, bl_user_id):
        user = cls.check_user(user_id)
        bl_user = session.query(UserPhotos).where(
            UserPhotos.user_id == bl_user_id
        ).first()
        user.blacklisted.append(bl_user)
        session.commit()


user_to_favorites = sq.Table('user_to_favorites', Base.metadata,
                             sq.Column('user_id', sq.Integer, sq.ForeignKey('user.user_id')),
                             sq.Column('fav_user_id', sq.Integer, sq.ForeignKey('user_photos.user_id'))
                             )

user_to_blacklisted = sq.Table('user_to_blacklisted', Base.metadata,
                               sq.Column('user_id', sq.Integer, sq.ForeignKey('user.user_id')),
                               sq.Column('bl_user_id', sq.Integer, sq.ForeignKey('user_photos.user_id'))
                               )


class UserPhotos(Base):

    __tablename__ = 'user_photos'

    user_id = sq.Column(
        sq.Integer,
        primary_key=True
    )
    firstname = sq.Column(sq.String)
    lastname = sq.Column(sq.String)
    user_photos = sq.Column(sq.Text)
    in_favorites = relationship(User, secondary='user_to_favorites', viewonly=True)
    in_blacklists = relationship(User, secondary='user_to_blacklisted', viewonly=True)

    @classmethod
    def check_user(cls, user_id):
        user = session.query(cls).where(
            cls.user_id == user_id
        ).first()
        if user is not None:
            return user
        return False

    @classmethod
    def add_user(cls, user_photos, firstname, lastname):
        # firstname, lastname = bot.get_fullname_for_founded_user(user_photos[0])
        print(user_photos)
        print(firstname)
        print(lastname)
        new_user = UserPhotos(
            user_id=user_photos[0],
            user_photos=user_photos[1],
            firstname=firstname,
            lastname=lastname
        )
        session.add(new_user)
        session.commit()
        # print('user' + str(user_photos[0]) + 'added to db with photos' + user_photos[1])


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


class City(Base):

    __tablename__ = 'cities'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    name = sq.Column(sq.String)


Base.metadata.create_all(engine)

