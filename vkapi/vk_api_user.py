import vk_api
from vk_api.tools import VkTools
from database.db_classes import FoundedUser, FoundedUsersCount, User
from decouple import config


class VkUser:

    user_token = config('USER_TOKEN')
    vk_user_session = vk_api.VkApi(token=user_token)
    tools = VkTools(vk_user_session)

    def find_users(self, user_id, params_id, offset=0, count=10, **parameters):
        '''
        находим пользователей по параметрам, переданным
        пользователем в **parameters. Обновляем количество
        найденных пользователей по определенным параметрам
        для передачи в offset
        '''
        users_list = []
        params = {'sort': 0,
                  'has_photo': 1,
                  'is_closed': False,
                  'fields': 'sex, city, relation, domain, bdate, home_town, has_photo',
                  'offset': offset,
                  'count': count
                  }
        users = self.vk_user_session.method('users.search', values={**params, **parameters})
        for user in users['items']:
            if user['is_closed'] or \
                    FoundedUser.get_user(user['id']) in User.get_user(user_id).blacklisted:
                continue
            users_list.append(user['id'])
        FoundedUsersCount.update_count(params_id, count)
        if len(users_list):
            return users_list
        return False

    def get_photos_for_founded_user(self, user_id):
        '''
        проверяем есть ли пользователь в БД.
        Если есть, получаем его фото из БД.
        Если нет, делаем запрос к API и получаем
        3 лучшие фото, добавляем в БД и возвращаем.
        '''
        user_in_db = FoundedUser.get_user(user_id)
        if user_in_db:
            user_photos = [user_in_db.user_id, user_in_db.user_photos]
            return user_photos
        user_photos = [user_id, []]
        default_values = {
            'album_id': 'profile',
            'extended': 1, 'photo_sizes': 1,
            'owner_id': user_id
        }
        photos = self.vk_user_session.method('photos.get', values=default_values)
        for photo in photos['items']:
            user_photos[1].append((
                        photo['likes']['count'],
                        f'photo{photo["owner_id"]}_{photo["id"]}'
                    ))
        if photos['count'] > 3:
            user_photos[1].sort(key=lambda x: (x[0], x[1]), reverse=True)
            user_photos[1] = user_photos[1][:3]
        user_photos[1] = ','.join([photo[1] for photo in user_photos[1]])
        return user_photos
