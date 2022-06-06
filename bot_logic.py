import re

from bot import bot, age_regex, keyboards, obj, count, user
from data import level_1, relation, level_2
from db import session, City


def bot_logic(users_list=None, search_params_id=None, current_user=None):
    while True:
        # uid, text, payload = bot.listen()
        uid, text = bot.listen()
        if text in level_1 or re.search(age_regex, text) \
                or session.query(City).where(City.name == text).first() is not None:
            start_logic(text, uid)
        elif text in level_2:
            advanced_logic(text, uid, users_list, search_params_id, current_user)
        elif text in ('избранное', 'далее', 'удалить'):
            fav_user = bot.get_user_in_favorites(uid, text, current_user)
            if not fav_user:
                bot.new_search(uid, keyboards.start_keyboard())
                return bot_logic()
            bot.show_pictures(
                uid,
                [fav_user.user_id, fav_user.user_photos],
                keyboards.user_link_keyboard(fav_user.user_id)
            )
            bot.make_decision_for_favorites(uid, keyboards.work_with_fav_keyboard())
            bot_logic(current_user=fav_user)

        elif text in ('черный список', 'следующий', 'удалить из чс'):
            bl_user = bot.get_user_in_blacklist(uid, text, current_user)
            if not bl_user:
                bot.new_search(uid, keyboards.start_keyboard())
                return bot_logic()
            bot.show_pictures(uid,
                              [bl_user.user_id, bl_user.user_photos],
                              keyboards.user_link_keyboard(bl_user.user_id)
                              )
            bot.make_decision_for_blacklist(uid, keyboards.work_with_bl_keyboard())
            bot_logic(current_user=bl_user)

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
    elif text in ('start', 'изменить параметры поиска'):
        bot.gender_choice(uid, keyboards.gender_keyboard())
    elif text == 'exit':
        bot.say_bye(uid, keyboards.exit_keyboard())
        count.clear_count(uid)
    elif text == 'menu':
        bot.show_menu(uid, keyboards.menu_keyboard())
    elif text == 'просмотреть параметры поиска':
        bot.show_parameters(uid, keyboards.before_searching_keyboard())
    else:
        bot.write_message(uid, f'{uid}, я тебя не понял попробуй еще')


def advanced_logic(text, uid, users_list, search_params_id, current_user):
    if text == 'найти':
        search_params_id = obj.add_search_params(user_id=uid, params=str(bot.search_parameters.setdefault(uid, {})))
        offset = count.check_count(uid, search_params_id)
        bot.founded_users[uid] = user.find_users(uid, search_params_id, offset=offset, **bot.search_parameters[uid])
        if not bot.founded_users[uid]:
            bot.new_search(uid, keyboards.new_search_keyboard())
            return bot_logic()
        user_photos = user.get_photos_for_founded_user(bot.founded_users[uid].pop(0))
        bot.show_pictures(uid, user_photos, keyboards.user_link_keyboard(user_photos[0]))
        bot.make_decision(uid, keyboards.decision_keyboard())
        return bot_logic(bot.founded_users[uid], search_params_id, user_photos[0])
    elif text in ('like', 'dislike', 'next'):
        bot.add_to_db(text, uid, current_user)
        try:
            user_photos = user.get_photos_for_founded_user(bot.founded_users[uid].pop(0))
            bot.show_pictures(uid, user_photos, keyboards.user_link_keyboard(user_photos[0]))
            bot.make_decision(uid, keyboards.decision_keyboard())
            print('bot.founded_users[uid]', bot.founded_users[uid])
        except IndexError:
            offset = count.check_count(uid, search_params_id)
            bot.founded_users[uid] = user.find_users(uid, search_params_id, offset=offset, **bot.search_parameters[uid])
            if not bot.founded_users[uid]:
                bot.new_search(uid, keyboards.new_search_keyboard())
                return bot_logic()
            user_photos = user.get_photos_for_founded_user(bot.founded_users[uid].pop(0))
            bot.show_pictures(uid, user_photos, keyboards.user_link_keyboard(user_photos[0]))
            bot.make_decision(uid, keyboards.decision_keyboard())
        finally:
            return bot_logic(bot.founded_users[uid], search_params_id, user_photos[0])


if __name__ == '__main__':
    bot_logic()

