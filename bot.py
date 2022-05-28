import os
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from data import relation_reverse, sex_reverse, parameters
import re

from db import SearchParams, FoundedUsersCount, User
from vk_user import VkUser
from keyboards import Keyboards


class VkBot:

    group_token = os.getenv('GROUP_TOKEN')
    vk_group_session = vk_api.VkApi(token=group_token)
    long_poll = VkLongPoll(vk_group_session)
    search_parameters = {}
    founded_users = {}

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
                payload = event.extra_values.get('payload')
                if payload is not None:
                    payload = eval(payload)[1]
                return user_id, text, payload

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
                                    ' для выхода, HELP для помощи', keyboard=keyboard)

    def say_bye(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(user_id, f'Пока {name}, жаль уходишь:( \nЖми "START" и начнем сначала.'
                                    f'"HELP" для помощи.', keyboard=keyboard)
        self.search_parameters.setdefault(user_id, {})

    @classmethod
    def get_fullname(cls, user_id):
        user_in_db = User.check_user(user_id)
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
        self.write_message(user_id, f'{name}, ты выбрал следующие параметры: \nПол: '
                                    f'{sex_reverse.get(self.search_parameters[user_id]["sex"], "Не выбран")}\n'
                                    f'Возраст от {self.search_parameters[user_id].get("age_from", "Не выбран")} '
                                    f'до {self.search_parameters[user_id].get("age_to", "Не выбран")} \n'
                                    f'Семейное положение: '
                                    f'{relation_reverse.get(self.search_parameters[user_id]["status"], "Не выбран")}\n'
                                    f'Город: {self.search_parameters[user_id].get("hometown", "Не выбран").title()}',
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
        name, surname = self.get_fullname(user_photos[0])
        self.write_message(
            user_id,
            f'Как тебе {name} {surname}?',
            attachment=user_photos[1],
            keyboard=keyboard)

    def new_search(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(
            user_id,
            f'{name}, пользователи закончились',
            keyboard=keyboard)


user = VkUser()
bot = VkBot()
keyboards = Keyboards()
obj = SearchParams()
count = FoundedUsersCount()
age_regex = r'^[0-9]{1,2}-?([0-9]{1,2})?'
