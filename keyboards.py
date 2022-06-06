from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Keyboards:

    @classmethod
    def age_choice(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('19-24')
        keyboard.add_button('25-29')
        keyboard.add_button('30-34')
        keyboard.add_button('35-39')
        return keyboard.get_keyboard()

    @classmethod
    def start_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('START', 'positive')
        keyboard.add_button('EXIT', 'negative')
        keyboard.add_button('MENU', 'primary')
        return keyboard.get_keyboard()

    @classmethod
    def exit_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('START', 'positive')
        keyboard.add_button('MENU', 'secondary')
        return keyboard.get_keyboard()

    @classmethod
    def menu_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('START', 'positive')
        keyboard.add_button('EXIT', 'negative')
        keyboard.add_line()
        keyboard.add_button('ПРОСМОТРЕТЬ ПАРАМЕТРЫ ПОИСКА', 'primary')
        keyboard.add_button('ИЗМЕНИТЬ ПАРАМЕТРЫ ПОИСКА', 'primary')
        keyboard.add_line()
        keyboard.add_button('ИЗБРАННОЕ', 'primary')
        keyboard.add_button('ЧЕРНЫЙ СПИСОК', 'primary')
        return keyboard.get_keyboard()

    @classmethod
    def gender_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('МУЖСКОЙ', 'primary')
        keyboard.add_button('ЖЕНСКИЙ', 'positive')
        return keyboard.get_keyboard()

    @classmethod
    def before_searching_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('НАЙТИ', 'positive')
        keyboard.add_line()
        keyboard.add_button('ИЗМЕНИТЬ ПАРАМЕТРЫ ПОИСКА', 'primary')
        keyboard.add_line()
        keyboard.add_button('EXIT', 'negative')
        return keyboard.get_keyboard()

    @classmethod
    def cities_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('МОСКВА', 'secondary')
        keyboard.add_button('САНКТ-ПЕТЕРБУРГ', 'secondary')
        keyboard.add_line()
        keyboard.add_button('КАЗАНЬ', 'secondary')
        keyboard.add_button('РОСТОВ-НА-ДОНУ', 'secondary')
        keyboard.add_line()
        keyboard.add_button('ЯРОСЛАВЛЬ', 'secondary')
        keyboard.add_button('КРАСНОДАР', 'secondary')
        return keyboard.get_keyboard()

    @classmethod
    def relation_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('замужем/женат', 'negative')
        keyboard.add_button('не замужем/не женат', 'positive')
        keyboard.add_line()
        keyboard.add_button('есть друг/есть подруга', 'primary')
        keyboard.add_button('в активном поиске', 'positive')
        return keyboard.get_keyboard()

    def user_link_keyboard(self, user_id):
        user_link = f'https://vk.com/id{user_id}'
        keyboard = VkKeyboard(one_time=False, inline=True)
        keyboard.add_openlink_button('Перейти на страницу пользователя', user_link)
        return keyboard.get_keyboard()

    @classmethod
    def decision_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('LIKE', 'positive')
        keyboard.add_button('DISLIKE', 'negative')
        keyboard.add_line()
        keyboard.add_button('NEXT', 'primary')
        keyboard.add_button('EXIT', 'negative')
        keyboard.add_line()
        keyboard.add_button('изменить параметры поиска', 'primary')
        return keyboard.get_keyboard()

    @classmethod
    def new_search_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('изменить параметры поиска', 'primary')
        keyboard.add_line()
        keyboard.add_button('EXIT', 'negative')
        keyboard.add_line()
        keyboard.add_button('MENU')
        return keyboard.get_keyboard()

    @classmethod
    def work_with_fav_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('ДАЛЕЕ', 'positive')
        keyboard.add_button('УДАЛИТЬ', 'negative')
        keyboard.add_line()
        keyboard.add_button('MENU')
        keyboard.add_button('START')
        return keyboard.get_keyboard()

    @classmethod
    def work_with_bl_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('СЛЕДУЮЩИЙ', 'positive')
        keyboard.add_button('УДАЛИТЬ ИЗ ЧС', 'negative')
        keyboard.add_line()
        keyboard.add_button('MENU')
        keyboard.add_button('START')
        return keyboard.get_keyboard()
