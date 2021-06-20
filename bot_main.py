import pandas
import vk_api

import constants   # This file is ignored by git
# It contains token and group id

import questions_list

from db import *
from api import *

from vk_api.longpoll import VkLongPoll, VkEventType


# Constants and preparations
TOKEN = constants.token
GROUP_ID = constants.group_id
ADMIN_IDS = constants.admin_ids
QUESTIONS = questions_list.questions

vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)

users = pandas.read_csv('users.csv', index_col='user_id')
# DB structure: user_id, bot_answers, score, step, way

quest = pandas.read_csv('quest.csv', index_col='step_id')
# DB structure: step_id, task, answer, score


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            users = check_user(users, event.user_id)
            request = event.text

            if request in ('Меню', 'Назад', 'Привет'):  # Calls usual menu
                users = change_user_data(users, event.user_id, 'bot_answers', 1)
                write_msg(event.user_id, 'Чего изволите?', 'default.json')

            elif request == 'Поговорить с человеком':  # Stops bot responses
                users = change_user_data(users, event.user_id, 'bot_answers', 0)
                write_msg(event.user_id, 'Мы ответим КТТС', 'menu_call.json')

            elif request in QUESTIONS.keys():  # For Ruslan
                write_msg(vk, event.user_id, QUESTIONS[request])

            elif request.startswith('http'):
                get_id(vk, request)

            elif get_user_data(users, event.user_id, 'bot_answers'):  # Usual response
                if request in ('Квест', 'Текущее задание', 'Следующее задание'):
                    if not check_subscription(vk, event.user_id, GROUP_ID):  # Checking if user is subscribed
                        message = 'Чтобы выполнять квест, подпишись на нашу группу'
                        write_msg(vk, event.user_id, message, 'default.json')
                    elif check_end(users, quest, event.user_id):  # Check if quest is already passed
                        score = get_user_data(users, event.user_id, "score")
                        message = f'Ты уже выполнил наш квест \nТы набрал {score} баллов'
                        write_msg(vk, event.user_id, message, 'default.json')
                    else:
                        send_task(vk, users, event.user_id)  # Just sending the task

                elif request == 'Баллы квеста':  # Returns quest score
                    score = get_user_data(users, event.user_id, "score")
                    score = int(score) if int(score) == score else score
                    message = f'У тебя {score} баллов, шик'
                    write_msg(event.user_id, message, 'default.json')

                elif request == 'Задать вопросы':
                    write_msg(event.user_id, 'Что хочешь узнать?', 'questions1.json')

                elif request.startswith('Страница '):
                    num = request[-1]
                    write_msg(vk, event.user_id, 'Что хочешь узнать?', f'questions{num}.json')

                elif check_answer(users, quest, event.user_id, request):
                    score_delta = get_quest_data(users, get_user_data(users, event.user_id, 'step'), 'score')
                    users = increase_value(users, event.user_id, 'score', score_delta)

                    specials = {'15': 22}

                    if str(request) in specials:
                        users = change_user_data(users, event.user_id, 'step', specials[str(request)])
                    else:
                        users = increase_value(users, event.user_id, 'step', 1)

                    if check_end(users, quest, event.user_id):
                        score = get_user_data(users, event.user_id, 'score')
                        write_msg(vk, event.user_id, f'Красава, всё прошёл \nУ тебя {score} баллов', 'default.json')

                else:
                    write_msg(event.user_id, f'Иди на хуй со своим "{request}", сука!', 'default.json')
