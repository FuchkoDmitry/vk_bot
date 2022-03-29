import os
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from data import sex, relation_reverse, relation, cities
import re


class VkBot:

    group_token = os.getenv('GROUP_TOKEN')
    vk_group_session = vk_api.VkApi(token=group_token)
    long_poll = VkLongPoll(vk_group_session)


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

    def write_message(self, user_id, message, **kwargs):
        post = {'user_id': user_id,
                'random_id': randrange(10 ** 7),
                'message': message
                }
        self.vk_group_session.method('messages.send',
                                     values={**post, **kwargs}
                                     )

    def say_hello(self, user_id):
        name, surname = self.get_fullname(user_id)
        keyboard = self.get_keyboard(user_id, (('START', 'positive'), ('EXIT', 'negative'), ('HELP', 'secondary')))
        self.write_message(user_id, f'Привет {name} {surname}, я бот, который поможет тебе'
                                    'найти пару. Жми START, чтобы начать, EXIT'
                                    ' для выхода, HELP для помощи', keyboard=keyboard)

    @classmethod
    def get_fullname(cls, user_id):
        request = cls.vk_group_session.method('users.get', values={'user_ids': user_id})[0]
        first_name = request['first_name']
        last_name = request['last_name']
        return first_name, last_name

    def get_age_for_search(self, user_id):
        name = self.get_fullname(user_id)[0]
        keyboard = self.get_keyboard(user_id, (
                                               ('19-24', 'secondary'),
                                               ('25-29', 'secondary'),
                                               ('30-34', 'secondary'),
                                               ('35-39', 'secondary')
                                               )
                                     )
        self.write_message(user_id,
                           f'{name} выбери диапазон возраста из '
                           f'предложенных или введи точный',
                           keyboard=keyboard
                           )

    def gender_choice(self, user_id):
        name = self.get_fullname(user_id)[0]
        keyboard = self.get_keyboard(user_id,
                                     (('МУЖСКОЙ', 'secondary'),
                                      ('ЖЕНСКИЙ', 'secondary')
                                      ),
                                     'sex'
                                     )
        self.write_message(user_id, f'{name} выбирай пол: ', keyboard=keyboard)

    def city_choice(self, user_id):
        name = self.get_fullname(user_id)[0]
        keyboard = self.get_keyboard(user_id, (
                                                ('МОСКВА', 'secondary'),
                                                ('САНКТ-ПЕТЕРБУРГ', 'secondary'),
                                                ('ADD', ''),
                                                ('КАЗАНЬ', 'secondary'),
                                                ('РОСТОВ-НА-ДОНУ', 'secondary'),
                                                ('ADD', ''),
                                                ('ЯРОСЛАВЛЬ', 'secondary'),
                                                ('КРАСНОДАР', 'secondary')
                                               )
                                     )
        self.write_message(user_id, f'{name} выбери город из списка, или введи другой',
                           keyboard=keyboard)

    def relation_choice(self, user_id):
        name = self.get_fullname(user_id)[0]
        print(relation_reverse[1], relation_reverse[2], relation_reverse[4], relation_reverse[6])
        keyboard = self.get_keyboard(user_id, ((relation_reverse[1], 'positive'),
                                               (relation_reverse[2], 'negative'),
                                               ('ADD', ''),
                                               (relation_reverse[4], 'primary'),
                                               (relation_reverse[6], 'secondary')),
                                     'relation')
        self.write_message(user_id, f'{name} выбирай семейное положение', keyboard=keyboard)

    def get_keyboard(self, user_id, buttons: tuple, payload=None, one_time=True):

        keyboard = VkKeyboard(one_time=one_time)
        if payload:
            payload = [user_id, payload]
        for button in buttons:
            if button[0] == 'ADD':
                keyboard.add_line()
            else:
                keyboard.add_button(button[0], color=button[1], payload=payload)
        return keyboard.get_keyboard()





search_parameters = dict()
bot = VkBot()
flag = 0
while True:
    uid, text, payload = bot.listen()
    print('payload:', payload)
    print('text:', text)
    if flag == 0 and text != 'start':
        bot.say_hello(uid)
        flag = 1
    if payload == 'sex':
        search_parameters['sex'] = sex[text]
        bot.get_age_for_search(uid)

    elif payload == 'relation':
        search_parameters['status'] = relation[text]
        bot.city_choice(uid)

    elif re.search(r'^(\d{1,2})(-\d{1,2})?', text):
        if int(text[:2]) < 18:
            bot.write_message(uid, 'Возраст должен быть больше 18. Введи еще раз!')
        else:
            search_parameters['age_from'] = int(text[:2])
            if len(text) == 2:
                search_parameters['age_to'] = int(text[:2]) + 1
            else:
                search_parameters['age_to'] = int(text[3:])
            bot.relation_choice(uid)

    elif text in cities:
        search_parameters['hometown'] = text.title()
        if len(search_parameters) == 5:
            print('заполнены все параметры поиска')

    elif text == 'start':
        bot.gender_choice(uid)
