import sqlalchemy.exc
import contextlib
from decouple import config

'''
создание БД Postgres. 
'''
db_login = config('DB_LOGIN')
db_password = config('DB_PASSWORD')
db_name = config('DB_NAME')

if __name__ == '__main__':
    with contextlib.suppress(sqlalchemy.exc.ProgrammingError):
        with sqlalchemy.create_engine(
                f'postgresql://{db_login}:{db_password}@localhost:5432',
                isolation_level='AUTOCOMMIT'
        ).connect() as connection:
            connection.execute(f'CREATE DATABASE {db_name}')
