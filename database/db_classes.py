
import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import and_
from decouple import config

Base = declarative_base()
db_login = config('DB_LOGIN')
db_password = config('DB_PASSWORD')
db_name = config('DB_NAME')


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
    favorites = relationship('FoundedUser', secondary='user_to_favorites')
    blacklisted = relationship('FoundedUser', secondary='user_to_blacklisted')

    @classmethod
    def get_user(cls, user_id):
        user = session.query(cls).where(
            cls.user_id == user_id
        ).first()
        if user is None:
            return False
        return user

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
        user = cls.get_user(user_id)
        fav_user = session.query(FoundedUser).where(
            FoundedUser.user_id == fav_user_id
        ).first()
        user.favorites.append(fav_user)
        session.commit()

    @classmethod
    def add_to_blacklist(cls, user_id, bl_user_id):
        user = cls.get_user(user_id)
        bl_user = session.query(FoundedUser).where(
            FoundedUser.user_id == bl_user_id
        ).first()
        user.blacklisted.append(bl_user)
        session.commit()

    @classmethod
    def get_favorites(cls, user_id):
        user = cls.get_user(user_id)
        return user.favorites

    @classmethod
    def delete_from_favorites(cls, user_id, user_to_delete):
        user = cls.get_user(user_id)
        user.favorites.remove(user_to_delete)
        session.commit()

    @classmethod
    def get_blacklisted(cls, user_id):
        user = cls.get_user(user_id)
        return user.blacklisted

    @classmethod
    def delete_from_blacklist(cls, user_id, user_to_delete):
        user = cls.get_user(user_id)
        user.blacklisted.remove(user_to_delete)
        session.commit()

    @classmethod
    def is_matched(cls, user_obj, fav_user_obj):
        if user_obj in fav_user_obj.favorites:
            return user_obj, fav_user_obj
        return False


user_to_favorites = sq.Table('user_to_favorites', Base.metadata,
                             sq.Column('user_id', sq.Integer, sq.ForeignKey('user.user_id')),
                             sq.Column('fav_user_id', sq.Integer, sq.ForeignKey('user_photos.user_id'))
                             )

user_to_blacklisted = sq.Table('user_to_blacklisted', Base.metadata,
                               sq.Column('user_id', sq.Integer, sq.ForeignKey('user.user_id')),
                               sq.Column('bl_user_id', sq.Integer, sq.ForeignKey('user_photos.user_id'))
                               )


class FoundedUser(Base):

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
    def get_user(cls, user_id):
        user = session.query(cls).where(
            cls.user_id == user_id
        ).first()
        if user is not None:
            return user
        return False

    @classmethod
    def add_user(cls, user_photos, firstname, lastname):
        new_user = FoundedUser(
            user_id=user_photos[0],
            user_photos=user_photos[1],
            firstname=firstname,
            lastname=lastname
        )
        session.add(new_user)
        session.commit()

    @classmethod
    def get_photos(cls, user_id):
        user = cls.get_user(user_id)
        return user.user_photos


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
            return self.id
        else:
            return request.id


class FoundedUsersCount(Base):

    __tablename__ = 'founded_users_count'

    searching_parameters_id = sq.Column(sq.Integer,
                                        sq.ForeignKey('searching_parameters.id'),
                                        primary_key=True
                                        )
    user_id = sq.Column(sq.Integer)
    founded_users_count = sq.Column(sq.Integer)

    def check_count(self, user_id, search_params_id):
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
