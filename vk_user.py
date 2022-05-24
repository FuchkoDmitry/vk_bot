import vk_api
import requests
import os
from vk_api.tools import VkTools


class VkUser:

    user_token = os.getenv('USER_TOKEN')
    vk_user_session = vk_api.VkApi(token=user_token)
    tools = VkTools(vk_user_session)

    def find_users(self, offset=0, count=10, **parameters):
        '''
        находим пользователей по параметрам, переданным
        пользователем в **parameters
        :param offset:
        :param count:
        :param parameters:
        :return:
        '''
        users_list = []
        params = {'sort': 0,
                  'has_photo': 1,
                  'is_closed': False,
                  'fields': 'sex, city, relation, domain, bdate, home_town',
                  'offset': offset
                  }

        users_iter = self.tools.get_all_iter('users.search', max_count=count, values={**params, **parameters})
        for user in users_iter:
            # if find_user_in_db(Users, user['id']) or user['is_closed'] or find_in_blacklisted(user['id'], user_id):
            if user['is_closed']:
                continue
            else:
                users_list.append(user['id'])
        if len(users_list) == 0:
            return False
        return users_list

    def get_photos_for_founded_users(self, user_list):
        user_photos = dict()

        default_values = {
            'album_id': 'profile',
            'extended': 1, 'photo_sizes': 1
        }

        users_photos, errors = vk_api.vk_request_one_param_pool(
            self.vk_user_session,
            'photos.get',
            key='user_id',
            values=user_list,
            default_values=default_values
        )
        print(users_photos)
        for user_id, data in users_photos.items():
            if data['count'] == 0:
                continue
            else:
                user_photos[user_id] = []
                for photo in data['items']:
                    user_photos[user_id].append((
                        photo['likes']['count'],
                        f'photo{photo["owner_id"]}_{photo["id"]}'
                    ))

            if data['count'] > 3:
                user_photos[user_id].sort(key=lambda x: (x[0], x[1]), reverse=True)
                user_photos[user_id] = user_photos[user_id][:3]
        print(user_photos)
        return user_photos


