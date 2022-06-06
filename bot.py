import os
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from data import relation_reverse, sex_reverse, parameters
import re

from db import SearchParams, FoundedUsersCount, User, FoundedUser
from vk_user import VkUser
from keyboards import Keyboards





class VkBot:

    group_token = os.getenv('GROUP_TOKEN')
    vk_group_session = vk_api.VkApi(token=group_token)
    long_poll = VkLongPoll(vk_group_session)
    search_parameters = {}
    founded_users = {}
    favorite_users = {}
    blacklist_users = {}

    def listen(self):
        '''
        бот слушает сервер. при получении сообщения,
        и возвращает user_id и текст сообщения. Если
        была передана payload информация, преобразует её
        в словарь и передает её вместо текста сообщения.
        '''
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()
                user_id = event.user_id
                # payload = event.extra_values.get('payload')
                # if payload is not None:
                #     payload = eval(payload)[1]
                # return user_id, text, payload
                return user_id, text

    def write_message(self, user_id, message, attachment=None, **kwargs):
        '''
        написать сообщение пользователю
        :param user_id: id пользователя
        :param message: текст сообщения
        :param attachment: вложение(опционально)
        :param kwargs:
        :return:
        '''
        post = {'user_id': user_id,
                'random_id': randrange(10 ** 7),
                'message': message
                }
        if attachment:
            post['attachment'] = attachment
        self.vk_group_session.method('messages.send',
                                     values={**post, **kwargs}
                                     )

    def say_hello(self, user_id, keyboard):

        name, surname = self.get_fullname(user_id)
        self.write_message(user_id, f'Привет {name} {surname}, я бот, который поможет тебе'
                                    'найти пару. Жми START, чтобы начать, EXIT'
                                    ' для выхода, MENU - посмотреть меню', keyboard=keyboard)

    def say_bye(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(user_id, f'Пока {name}, жаль уходишь:( \nЖми "START" и начнем сначала.'
                                    f'"MENU" для помощи.', keyboard=keyboard)
        self.search_parameters.setdefault(user_id, {})
        self.founded_users.setdefault(user_id, [])

    def show_menu(self, user_id, keyboard):
        self.write_message(user_id,
                           'START - начать новый поиск. EXIT - выйти.'
                           'ПРОСМОТРЕТЬ ПАРАМЕТРЫ ПОИСКА - посмотреть свои '
                           'текущие параметры поиска. ИЗБРАННОЕ - '
                           'посмотреть пользователей, которых ты "лайкнул". '
                           'ЧЕРНЫЙ СПИСОК - посмотреть кому ты поставил "дизлайк".',
                           keyboard=keyboard)

    @classmethod
    def get_fullname(cls, user_id):
        user_in_db = User.get_user(user_id)
        if user_in_db:
            first_name = user_in_db.firstname
            last_name = user_in_db.lastname
            # print(user_in_db, first_name, last_name)
            return first_name, last_name

        request = cls.vk_group_session.method('users.get', values={'user_ids': user_id})[0]
        first_name = request['first_name']
        last_name = request['last_name']
        User.add_user(user_id, first_name, last_name)
        return first_name, last_name

    @classmethod
    def get_fullname_for_founded_user(cls, founded_user_id):
        user_in_db = FoundedUser.get_user(founded_user_id[0])
        if not user_in_db:
            request = cls.vk_group_session.method('users.get', values={'user_ids': founded_user_id[0]})[0]
            first_name = request['first_name']
            last_name = request['last_name']
            FoundedUser.add_user(founded_user_id, first_name, last_name)
            return first_name, last_name
        first_name = user_in_db.firstname
        last_name = user_in_db.lastname
        # print(user_in_db, first_name, last_name)
        return first_name, last_name

    def get_age_for_search(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(user_id,
                           f'{name} выбери диапазон возраста из '
                           f'предложенных или введи точный. Возраст'
                           f'должен быть больше от 18 лет до 55.',
                           keyboard=keyboard
                           )

    def gender_choice(self, user_id, keyboard):
        self.search_parameters[user_id] = {}
        name = self.get_fullname(user_id)[0]
        self.write_message(user_id, f'{name} выбирай пол: ', keyboard=keyboard)

    def show_parameters(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        params = self.search_parameters.setdefault(user_id, {})
        self.write_message(user_id, f'{name}, ты выбрал следующие параметры: \nПол: '
                                    f'{sex_reverse.get(params.get("sex"), "Не выбран")}\n'
                                    f'Возраст от {params.get("age_from", "--")} '
                                    f'до {params.get("age_to", "--")} \n'
                                    f'Семейное положение: '
                                    f'{relation_reverse.get(params.get("status"), "Не выбрано")}\n'
                                    f'Город: {params.get("hometown", "Не выбран").title()}',
                                    keyboard=keyboard)

    def city_choice(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(user_id, f'{name} выбери город из списка, или введи другой',
                           keyboard=keyboard)

    def relation_choice(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(user_id, f'{name} выбирай семейное положение', keyboard=keyboard)

    def make_decision(self, user_id, keyboard):
        self.write_message(user_id,
                           'нравится - LIKE, не нравится - DISLIKE, '
                           'NEXT - смотреть дальше, EXIT - в главное '
                           'меню или изменить параметры поиска - ',
                           keyboard=keyboard
                           )

    def make_decision_for_favorites(self, user_id, keyboard):
        self.write_message(user_id,
                           'ДАЛЕЕ - просмотреть следующего пользователя. \n'
                           'УДАЛИТЬ - удалить пользователя из избранного. \n'
                           'MENU - вернуться в меню. \n'
                           'START - начать новый поиск.',
                           keyboard=keyboard)

    def make_decision_for_blacklist(self, user_id, keyboard):
        self.write_message(user_id,
                           'СЛЕДУЮЩИЙ - просмотреть следующего пользователя. \n'
                           'УДАЛИТЬ ИЗ ЧС - удалить пользователя из черного списка. \n'
                           'MENU - вернуться в меню. \n'
                           'START - начать новый поиск.',
                           keyboard=keyboard)

    def check_age(self, user_id, text):
        if int(text[:2]) < 18:
            self.get_age_for_search(user_id, keyboards.age_choice())
            return False
        else:
            self.set_parameters(user_id, text, 'hometown')
            return True

    def set_parameters(self, user_id, text, parameter):
        self.search_parameters.setdefault(user_id, {})
        # print(self.search_parameters.setdefault(user_id, {}))
        if re.search(r'^[0-9]{1,3}', text):
            self.search_parameters[user_id]['age_from'] = int(text[:2])
            if len(text) == 2:
                self.search_parameters[user_id]['age_to'] = int(text[:2]) + 1
            else:
                self.search_parameters[user_id]['age_to'] = int(text[3:])
        elif parameter == 'hometown':
            self.search_parameters[user_id][parameter] = text
        else:
            self.search_parameters[user_id][parameter] = parameters[text]

    def show_pictures(self, user_id, user_photos, keyboard):
        name, surname = self.get_fullname_for_founded_user(user_photos)
        self.write_message(
            user_id,
            f'Как тебе {name} {surname}?',
            attachment=user_photos[1],
            keyboard=keyboard)

    def new_search(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(
            user_id,
            f'{name}, пользователи закончились.\n '
            f'START - начать новый поиск. EXIT - выход. MENU - перейти в меню',
            keyboard=keyboard)

    # @classmethod
    def add_to_db(self, text, user_id, founded_user_id):
        if text == 'like':
            fav_user = FoundedUser.get_user(founded_user_id)
            if fav_user in User.get_user(user_id).favorites:
                self.write_message(user_id, 'Пользователь уже в вашем избранном')
                return False
            User.add_favorite(user_id, founded_user_id)
        elif text == 'dislike':
            User.add_to_blacklist(user_id, founded_user_id)

    def get_user_in_favorites(self, user_id, text, current_user=None):
        if text == 'удалить' and current_user is not None:
            User.delete_from_favorites(user_id, current_user)
        if not self.favorite_users.get(user_id, False):
            fav_users = User.get_favorites(user_id)
            self.favorite_users[user_id] = iter(fav_users)
        try:
            favorite_user = next(self.favorite_users[user_id])
            return favorite_user
            # return [favorite_user.user_id, favorite_user.user_photos]
        except StopIteration:
            self.favorite_users[user_id] = False
            return False

    def get_user_in_blacklist(self, user_id, text, current_user=None):
        if text == 'удалить из чс' and current_user is not None:
            User.delete_from_blacklist(user_id, current_user)
        if not self.blacklist_users.get(user_id, False):
            bl_users = User.get_blacklisted(user_id)
            self.blacklist_users[user_id] = iter(bl_users)
        try:
            blacklist_user = next(self.blacklist_users[user_id])
            return blacklist_user
        except StopIteration:
            self.blacklist_users[user_id] = False
            return False


user = VkUser()
bot = VkBot()
keyboards = Keyboards()
obj = SearchParams()
count = FoundedUsersCount()
age_regex = r'^[0-9]{1,2}-?([0-9]{1,2})?'
