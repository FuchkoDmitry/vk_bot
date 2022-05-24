import os
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from data import sex, relation_reverse, relation, sex_reverse, parameters, level_1
import re

from db import session, City, Base, engine
from vk_user import VkUser
from keyboards import Keyboards


class VkBot:

    group_token = os.getenv('GROUP_TOKEN')
    vk_group_session = vk_api.VkApi(token=group_token)
    long_poll = VkLongPoll(vk_group_session)
    search_parameters = {}

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
        del self.search_parameters[user_id]

    @classmethod
    def get_fullname(cls, user_id):
        request = cls.vk_group_session.method('users.get', values={'user_ids': user_id})[0]
        first_name = request['first_name']
        last_name = request['last_name']
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

    def check_age(self, user_id, text):
        if int(text[:2]) < 18:
            self.get_age_for_search(user_id, keyboard.age_choice())
            return False
        else:
            self.set_parameters(user_id, text, 'hometown')
            return True

    def set_parameters(self, user_id, text, parameter):
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


bot = VkBot()
keyboard = Keyboards()
age_regex = r'^[0-9]{1,2}-?([0-9]{1,2})?'
# Base.metadata.create_all(engine)
flag = 0
while True:
    uid, text, payload = bot.listen()
    print()
    print('payload=', payload)
    print('text=', text)
    if text in level_1 or re.search(age_regex, text) \
            or session.query(City).where(City.name == text).first() is not None:

        if text in {'мужской', 'женский'}:
            bot.set_parameters(uid, text, 'sex')
            bot.get_age_for_search(uid, keyboard.age_choice())
            print(bot.search_parameters[uid])
        elif text in relation:
            bot.set_parameters(uid, text, 'status')
            bot.city_choice(uid, keyboard.cities_keyboard())
            print(bot.search_parameters[uid])
        elif re.search(age_regex, text):
            is_checked = bot.check_age(uid, text)
            if is_checked:
                bot.relation_choice(uid, keyboard.relation_keyboard())
            print(bot.search_parameters[uid])
        elif session.query(City).where(City.name == text).first() is not None:
            bot.set_parameters(uid, text, 'hometown')
            bot.show_parameters(uid, keyboard.before_searching_keyboard())
            print(bot.search_parameters[uid])
        elif text in ('start', 'изменить параметры поиска'):
            bot.gender_choice(uid, keyboard.gender_keyboard())
            print(bot.search_parameters.setdefault(uid, {}))
        elif text == 'exit':
            bot.say_bye(uid, keyboard.exit_keyboard())
        else:
            bot.write_message(uid, f'{uid}, я тебя не понял попробуй еще')
    else:
        bot.say_hello(uid, keyboard.start_keyboard())


    '''   
     elif text == 'начать поиск':
        bot.write_message(uid, 'как тебе?', attachment='photo274665144_457239079,photo90114682_437813800,photo13458042_456239855,photo13458042_410551385,photo65021859_285038362')
        vk_user = VkUser()
        print(bot.search_parameters[uid])
        users = vk_user.find_users(**bot.search_parameters[uid])
        vk_user.get_photos_for_founded_users(users)
        '''
