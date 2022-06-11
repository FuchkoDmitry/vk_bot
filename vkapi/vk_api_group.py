from decouple import config
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_bot.data import relation_reverse, sex_reverse, parameters
import re
from database.db_classes import User, FoundedUser
from vk_bot.keyboards import Keyboards


class VkBot:

    group_token = config('GROUP_TOKEN')
    vk_group_session = vk_api.VkApi(token=group_token)
    long_poll = VkLongPoll(vk_group_session)
    search_parameters = {}
    founded_users = {}
    favorite_users = {}
    blacklist_users = {}

    def listen(self):
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text.lower()
                user_id = event.user_id
                return user_id, text

    def write_message(self, user_id, message, attachment=None, **kwargs):
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
        self.write_message(user_id, f'Привет {name} {surname}, я бот, который поможет тебе '
                                    'найти пару. Жми START, чтобы начать новый поиск,'
                                    ' MENU - посмотреть меню', keyboard=keyboard)

    def say_bye(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(user_id, f'Пока {name}, жаль уходишь:( \nЖми "START" и начнем сначала.'
                                    f'"MENU" для помощи.', keyboard=keyboard)
        self.search_parameters.setdefault(user_id, {})
        self.founded_users.setdefault(user_id, [])

    def show_menu(self, user_id, keyboard):
        self.write_message(user_id,
                           'START - начать новый поиск. EXIT - выйти. '
                           'ПРОСМОТР ПАРАМЕТРОВ - посмотреть свои '
                           'текущие параметры поиска. ИЗМЕНИТЬ ПАРАМЕТРЫ - '
                           'изменить параметры поиска. ИЗБРАННОЕ - '
                           'посмотреть пользователей, которых ты "лайкнул". '
                           'ЧЕРНЫЙ СПИСОК - посмотреть кому ты поставил "дизлайк".',
                           keyboard=keyboard)

    @classmethod
    def get_fullname(cls, user_id):
        user_in_db = User.get_user(user_id)
        if user_in_db:
            first_name = user_in_db.firstname
            last_name = user_in_db.lastname
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
        return first_name, last_name

    def get_age_for_search(self, user_id, keyboard):
        name = self.get_fullname(user_id)[0]
        self.write_message(user_id,
                           f'{name} выбери диапазон возраста из '
                           f'предложенных, выбери свой диапазон(через пробел или дефис)'
                           f' или введи точный. Возраст'
                           f' должен быть больше от 18 лет до 55.',
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
                           'меню или изменить параметры',
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
        if int(text[:2]) not in range(18, 56) or (len(text) in (3, 4) or len(text) > 5):
            self.get_age_for_search(user_id, Keyboards.age_choice())
            return False
        else:
            self.set_parameters(user_id, text, 'hometown')
            return True

    def set_parameters(self, user_id, text, parameter):
        self.search_parameters.setdefault(user_id, {})
        if re.search(r'^[0-9]{1,2}', text):
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

    def add_to_db_and_check_matched(self, text, user_id, founded_user_id):
        '''
        Добавляет пользователей в избранное и чс.
        При добавлении в избранное проверяет на
        совпадание пары.
        '''
        if founded_user_id is None:
            return False
        if text == 'like':
            user = User.get_user(user_id)
            fav_user = FoundedUser.get_user(founded_user_id)
            if fav_user in user.favorites:
                self.write_message(user_id, 'Пользователь уже в вашем избранном')
                return False
            # elif User.get_user(founded_user_id):
            User.add_favorite(user_id, founded_user_id)
            fav_user = User.get_user(founded_user_id)
            if fav_user:
                user = FoundedUser.get_user(user_id)
                return User.is_matched(user, fav_user)
        elif text == 'dislike':
            User.add_to_blacklist(user_id, founded_user_id)

    def messages_to_matched_users(self, user, matched_user):
        user_photos = FoundedUser.get_photos(user.user_id)
        self.write_message(user.user_id, f'{matched_user.lastname} {matched_user.firstname} '
                                         f'тоже лайкнул(а) тебя. Договориться о встрече или '
                                         f'продолжить просмотр?',
                           keyboard=Keyboards.write_message_to_fav_user(matched_user.user_id))
        self.write_message(matched_user.user_id, f'{user.lastname} {user.firstname} '
                                                 f'тоже лайкнул(а) тебя. Договоришься встретиться?',
                           keyboard=Keyboards.message_to_pair(user.user_id),
                           attachment=user_photos)

    def get_user_in_favorites(self, user_id, text, current_user=None):
        '''
        Выдает или удаляет пользователя из избранного.
        '''
        if text == 'удалить' and current_user is not None:
            User.delete_from_favorites(user_id, current_user)
        if not self.favorite_users.get(user_id, False):
            fav_users = User.get_favorites(user_id)
            self.favorite_users[user_id] = iter(fav_users)
        try:
            favorite_user = next(self.favorite_users[user_id])
            return favorite_user
        except StopIteration:
            self.favorite_users[user_id] = False
            return False

    def get_user_in_blacklist(self, user_id, text, current_user=None):
        '''
        Выдает или удаляет пользователя из чс.
        '''
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
