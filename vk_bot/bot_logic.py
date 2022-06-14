import re
from vkapi.vk_api_group import VkBot
from vkapi.vk_api_user import VkUser
from vk_bot.keyboards import Keyboards
from database.db_classes import SearchParams, FoundedUsersCount

from vk_bot.data import level_1, relation
from database.db_classes import session, City


bot = VkBot()
user = VkUser()
keyboards = Keyboards()
obj = SearchParams()
count = FoundedUsersCount()
age_regex = r'^[0-9]{1,2}-?([0-9]{1,2})?'


def start_bot(users_list=None, search_params_id=None, current_user=None):

    while True:
        uid, text = bot.listen()
        if text in level_1 or re.search(age_regex, text) \
                or session.query(City).where(City.name == text).first() is not None:
            start_logic(text, uid)
        elif text in ('найти', 'next', 'like', 'dislike'):
            advanced_logic(text, uid, users_list, search_params_id, current_user)
        elif text in ('избранное', 'далее', 'удалить'):
            fav_user = bot.get_user_in_favorites(uid, text, current_user)
            if not fav_user:
                bot.new_search(uid, keyboards.start_keyboard())
                return start_bot()
            bot.show_pictures(
                uid,
                [fav_user.user_id, fav_user.user_photos],
                keyboards.user_link_keyboard(fav_user.user_id)
            )
            bot.make_decision_for_favorites(uid, keyboards.work_with_fav_keyboard())
            start_bot(current_user=fav_user)

        elif text in ('черный список', 'следующий', 'удалить из чс'):
            bl_user = bot.get_user_in_blacklist(uid, text, current_user)
            if not bl_user:
                bot.new_search(uid, keyboards.start_keyboard())
                return start_bot()
            bot.show_pictures(uid,
                              [bl_user.user_id, bl_user.user_photos],
                              keyboards.user_link_keyboard(bl_user.user_id)
                              )
            bot.make_decision_for_blacklist(uid, keyboards.work_with_bl_keyboard())
            start_bot(current_user=bl_user)

        else:
            bot.say_hello(uid, keyboards.start_keyboard())


def start_logic(text, uid):
    if text in {'мужской', 'женский'}:
        bot.set_parameters(uid, text, 'sex')
        bot.get_age_for_search(uid, keyboards.age_choice())
    elif text in relation:
        bot.set_parameters(uid, text, 'status')
        bot.city_choice(uid, keyboards.cities_keyboard())
    elif re.search(age_regex, text):
        is_checked = bot.check_age(uid, text)
        if is_checked:
            bot.relation_choice(uid, keyboards.relation_keyboard())
    elif session.query(City).where(City.name == text).first() is not None:
        bot.set_parameters(uid, text, 'hometown')
        bot.show_parameters(uid, keyboards.before_searching_keyboard())
    elif text in ('start', 'изменить параметры'):
        bot.gender_choice(uid, keyboards.gender_keyboard())
    elif text == 'exit':
        bot.say_bye(uid, keyboards.exit_keyboard())
    elif text == 'menu':
        bot.show_menu(uid, keyboards.menu_keyboard())
    elif text == 'просмотр параметров':
        bot.show_parameters(uid, keyboards.before_searching_keyboard())
    else:
        bot.write_message(uid, 'я тебя не понял попробуй еще')


def advanced_logic(text, uid, users_list, search_params_id, current_user):
    if text == 'найти' or len(bot.founded_users.get(uid, [])) == 0:
        search_params_id = obj.add_search_params(user_id=uid, params=str(bot.search_parameters.setdefault(uid, {})))
        offset = count.check_count(uid, search_params_id)
        bot.founded_users[uid] = user.find_users(uid, search_params_id, offset=offset, **bot.search_parameters[uid])
        if not bot.founded_users[uid]:
            count.clear_count(uid, search_params_id)
            bot.new_search(uid, keyboards.new_search_keyboard())
            return start_bot()
    is_matched = bot.add_to_db_and_check_matched(text, uid, current_user)
    if is_matched:
        bot.messages_to_matched_users(is_matched[0], is_matched[1])
        start_bot(bot.founded_users[uid], search_params_id, current_user)
    user_photos = user.get_photos_for_founded_user(bot.founded_users[uid].pop(0))
    bot.show_pictures(uid, user_photos, keyboards.user_link_keyboard(user_photos[0]))
    bot.make_decision(uid, keyboards.decision_keyboard())
    return start_bot(bot.founded_users[uid], search_params_id, user_photos[0])
