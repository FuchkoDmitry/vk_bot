import os
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

group_token = os.getenv('GROUP_TOKEN')
vk_group_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_group_session)


# def write_message(user_id, message='', keyboards=None, attachment=None):
def write_message(user_id, message, **kwargs):
    post = {'user_id': user_id,
            'random_id': randrange(10 ** 7),
            'message': message
            }
    print(kwargs)
    # if message:
    #     post['message'] = message

    # if keyboards:
    #     post['keyboards'] = keyboards.get_keyboard()
    #
    # if attachment:
    #     post['attachment'] = attachment

    vk_group_session.method('messages.send', values={**post, **kwargs})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        text = event.text.lower()
        uid = event.user_id
        payload = event.extra_values.get('payload')
        print(type(payload), '>', payload)
        # print('event.type:', event.type)
        print('event.text:', event.text)
        print('event.userid:', event.user_id)

        try:
            print('type_extra_values1', type(event.extra_values['payload']))
            print('extra_values2', eval(event.extra_values['payload']))
            print('type_after_eval_extra_values2', type(eval(event.extra_values['payload'])))


            print('raw', event.raw[6])
        except:
            print('no extra values')
        print('========')
        keyboard = VkKeyboard()
        # keyboards.add_button('button1', payload="test_flg")
        keyboard.add_button('button_2', payload={"hi": uid})
        keyboard.add_button('button_3', payload={"favorite": uid})
        keyboard.add_button('button_4', payload={"black": uid})
        keyboard.add_button('button_5', payload={'city': uid})
        print(keyboard.get_keyboard())

        write_message(uid, 'text_message', keyboard=keyboard.get_keyboard())





