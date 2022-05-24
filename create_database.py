import sqlalchemy
import sqlalchemy.exc
import contextlib
import os

'''
создание БД Postgres. 
'''
db_login = os.getenv('db_login')
db_password = os.getenv('db_password')
db_name = os.getenv('db_name')

if __name__ == '__main__':
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        with sqlalchemy.create_engine(
                f'postgresql://{db_login}:{db_password}@localhost:5432',
                isolation_level='AUTOCOMMIT'
        ).connect() as connection:
            connection.execute(f'CREATE DATABASE {db_name}')
