
'''
Заполнение таблицы City БД.
'''

if __name__ == '__main__':
    import csv
    from db import session, City, Base, engine
    Base.metadata.create_all(engine)
    csv.register_dialect('custom_csv', delimiter=';')

    with open('cities_list.csv', encoding='utf-8') as file:
        reader = csv.reader(file, 'custom_csv')
        for cities in list(reader)[1:]:
            city_to_add = cities[0].lower()
            city = City(name=city_to_add)
            session.add(city)
            session.commit()
