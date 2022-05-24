from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Keyboards:
    # keyboard = VkKeyboard(one_time=True)

    def age_choice(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('19-24')
        keyboard.add_button('25-29')
        keyboard.add_button('30-34')
        keyboard.add_button('35-39')
        return keyboard.get_keyboard()

    def start_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('START', 'positive')
        keyboard.add_button('EXIT', 'negative')
        keyboard.add_button('MENU', 'primary')
        return keyboard.get_keyboard()

    def exit_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('START', 'positive')
        keyboard.add_button('HELP', 'secondary')
        return keyboard.get_keyboard()

    def gender_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('МУЖСКОЙ', 'primary')
        keyboard.add_button('ЖЕНСКИЙ', 'positive')
        return keyboard.get_keyboard()

    def before_searching_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('НАЧАТЬ ПОИСК', 'positive')
        keyboard.add_line()
        keyboard.add_button('ИЗМЕНИТЬ ПАРАМЕТРЫ ПОИСКА', 'primary')
        keyboard.add_line()
        keyboard.add_button('EXIT', 'negative')
        return keyboard.get_keyboard()

    def cities_keyboard(self):
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

    def relation_keyboard(self):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('замужем/женат', 'negative')
        keyboard.add_button('не замужем/не женат', 'positive')
        keyboard.add_line()
        keyboard.add_button('есть друг/есть подруга', 'primary')
        keyboard.add_button('в активном поиске', 'positive')
        return keyboard.get_keyboard()
