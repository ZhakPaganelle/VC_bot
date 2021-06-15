import vk_api
from random import randint
from vk_api.longpoll import VkLongPoll, VkEventType


token = open('api_key.txt').read()
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randint(10**5, 10**6)})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            write_msg(event.user_id, f'Иди на хуй со своим "{request}"!')
