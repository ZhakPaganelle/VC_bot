import json
import random
import vk_api
import requests

import constants   # This file is ignored by git
                   # It contains token and group id

import questions_list
from quest import *
from users import *

from random import randint
from vk_api.longpoll import VkLongPoll, VkEventType


# Constants and preparations
TOKEN = constants.token
GROUP_ID = constants.group_id
SERVICE_KEY = constants.service_key
QUESTIONS = questions_list.questions
subscribe_message = constants.subscribe_message

vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)


# Working with vk api
def write_msg(user_id, message, keyboard_file=None, attachment=None):
    """
    Sends message to user

    :param user_id:
    :param message:
    :param keyboard_file: Bottom keyboard
    :param attachment:
    :return: No return
    """
    params = {'user_id': user_id, 'message': message, 'random_id': randint(10**5, 10**6)}
    if keyboard_file:
        keyboard = open(f'keyboards/{keyboard_file}', encoding='utf-8').read()
        params['keyboard'] = keyboard
    if attachment:
        params['attachment'] = attachment
    vk.method('messages.send', params)


def check_subscription(user_id, group_id):
    '''
    Checks if user is subscribed to given group

    :param user_id:
    :param group_id:
    :return: True if subscribed
    '''
    return vk.method('groups.isMember', {'group_id': group_id, 'user_id': user_id})


def get_id(link):
    link = link.split('/')[-1]
    data = vk.method('users.get', {'user_ids': link, 'fields': 'uid'})

    return data[0]['id']


def send_task(user_id):
    '''
    Sends current quest task to the given user
    :param user_id:
    :return:
    '''
    step = users_dict[user_id].step
    attacment_dict = {
        2: 'photo-194815411_457239018',
        3: 'photo-194815411_457239019,photo-194815411_457239020'
    }
    attachment = attacment_dict[step] if step in attacment_dict else None
    task = quest_list[step].text
    write_msg(user_id, task, 'quest.json', attachment)


def check_answer(user_id, request):
    '''
    Checks if user message is the same as the right answer
    :param user_id:
    :param request:
    :return:
    '''
    step = users_dict[user_id].step
    question = quest_list[step]
    if question.answer:
        return request.lower() == question.answer.lower()
    return False


def check_end(user_id):
    """
    Checks if user already completed the quest
    :param user_id:
    :return:
    """
    step = users_dict[user_id].step
    return step == len(quest_list)


def next_task(current_user):
    user_id = current_user.user_id
    if not check_end(user_id):
        write_msg(user_id, 'Красава')
        send_task(user_id)
    else:
        score = current_user.score
        score = int(score) if int(score) == score else score  # TODO: Use this
        write_msg(user_id, f'Красава, всё пройдено \nУ тебя {score} баллов', 'default.json')


def get_posts(community_id):
    params = {
        'owner_id': f'-{community_id}',
        'domain': f'https://vk.com/club{community_id}',
        'access_token': SERVICE_KEY,
        'v': 5.131
    }
    url = 'https://api.vk.com/method/wall.get'
    r = requests.get(url=url, params=params)
    posts = json.loads(r.text)['response']['items']
    return [post['id'] for post in posts]


def get_likes(community_id, post_id):
    params = {
        'type': 'post',
        'owner_id': f'-{community_id}',
        'item_id': post_id,
        'access_token': SERVICE_KEY,
        'v': 5.131
    }
    url = 'https://api.vk.com/method/likes.getList'
    r = requests.get(url=url, params=params)
    return json.loads(r.text)['response']['items']


def get_users_liked(community_id):
    users_liked = []
    posts_ids = get_posts(community_id)
    for post_id in posts_ids:
        users_liked.extend(get_likes(community_id, post_id))
    return users_liked


def check_likes(user):
    user_id = user.user_id
    likes = get_users_liked(GROUP_ID)
    return likes.count(user_id)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            users, users_dict = check_user(event.user_id)
            request = event.text

            if event.user_id in admins_dict.keys():
                if request.startswith('http'):  # Adding points to user
                    user_id = get_id(request)
                    admins_dict[event.user_id].change_last_checked(user_id)

                    current_user = users_dict[user_id]
                    if (value := quest_list[current_user.step].score) <= 10:  # If no score choice
                        current_user.change_score(quest_list[current_user.step].score)
                        current_user.change_step()

                        next_task(current_user)
                        write_msg(event.user_id, 'Готово')
                    else:
                        value = str(value)
                        write_msg(event.user_id, 'Сколько начислять?', f'{value}.json')

                elif len(request) == 1 and request.isnumeric():
                    current_user = users_dict[admins_dict[event.user_id].last_checked]
                    current_user.change_step()
                    current_user.change_score(int(request))

                    next_task(current_user)
                    write_msg(event.user_id, 'Готово')

            user_id = event.user_id
            current_user = users_dict[user_id]
            if current_user.step == 1:
                if check_likes(current_user) >= 1:
                    current_user.change_score(quest_list[current_user.step].score)
                    current_user.change_step()

                    next_task(current_user)
                else:
                    print(check_likes(current_user))

            elif check_answer(user_id, request):
                current_user.change_score(quest_list[current_user.step].score)
                current_user.change_step()

                next_task(current_user)

            elif request in ('Привет', 'Меню', 'Назад') or request.lower().startswith('привет'):  # Calls usual menu
                write_msg(user_id, 'Чего изволите?', 'default.json')

            elif request in ('Квест', 'Текущее задание', 'Следующее задание'):
                if not check_subscription(user_id, GROUP_ID):  # Checking if user is subscribed
                    write_msg(user_id, subscribe_message, 'default.json')
                elif check_end(user_id):  # Check if quest is already passed
                    score = current_user.score
                    score = int(score) if int(score) == score else score
                    message = f'Ты уже выполнил наш квест \nТы набрал {score} баллов'
                    write_msg(user_id, message, 'default.json')
                else:
                    send_task(user_id)  # Just sending the task

            elif request == 'Баллы':  # Returns quest score
                score = current_user.score
                score = int(score) if int(score) == score else score
                message = f'У тебя {score} баллов, шик'
                write_msg(user_id, message, 'default.json')

            # FAQ block
            elif request == 'Задать вопросы':
                write_msg(user_id, 'Что хочешь узнать?', 'questions1.json')

            elif request.startswith('Страница '):
                num = request[-1]
                write_msg(user_id, 'Что хочешь узнать?', f'questions{num}.json')

            elif request in QUESTIONS.keys():  # For Ruslan
                write_msg(user_id, QUESTIONS[request])
