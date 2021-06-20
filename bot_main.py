import pandas
import vk_api

import constants   # This file is ignored by git
# It contains token and group id

import questions_list

from random import randint
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


# Working with db
def check_user(user_id):
    '''
    Checks if user is in the BD
    If not, creates him there
    :param user_id:
    :return:
    '''

    if user_id not in set(users.index):
        new_user = [1, 0, 0, 'course']
        users.loc[user_id, :] = new_user
        print(users)
        users.to_csv('users.csv', encoding='utf-8')

    return users


def get_user_data(user_id, field):
    '''
    Returns field in given user row
    :param user_id:
    :param field:
    :return:
    '''
    return users.loc[user_id, field]


def change_user_data(user_id, field, value):
    '''
    Changes field value to value param
    :param user_id:
    :param field:
    :param value:
    :return:
    '''
    users.loc[user_id, field] = value
    users.to_csv('users.csv', encoding='utf-8')

    return users


def increase_value(user_id, field, delta):
    '''
    Increases field param by delta
    :param user_id:
    :param field:
    :param delta:
    :return:
    '''
    current_value = get_user_data(user_id, field)
    new_value = current_value + delta
    change_user_data(user_id, field, new_value)

    return users


def get_quest_data(step_id, field):
    '''
    Returns value of the field in quest
    :param step_id:
    :param field:
    :return:
    '''
    return quest.loc[step_id, field]


# Working with vk api
def write_msg(user_id, message, keyboard_file=None):
    '''
    Sends message to user

    :param user_id:
    :param message:
    :param keyboard_file: Bottom keyboard
    :return: No return
    '''
    params = {'user_id': user_id, 'message': message, 'random_id': randint(10**5, 10**6)}
    if keyboard_file:
        keyboard = open(f'keyboards/{keyboard_file}', encoding='utf-8').read()
        params['keyboard'] = keyboard
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
    print(vk.method('users.get', {'user_ids': link, 'fields': 'uid'}))


def send_task(user_id):
    '''
    Sends current quest task to the given user
    :param user_id:
    :return:
    '''
    step = get_user_data(user_id, 'step')
    task = get_quest_data(step, 'task')
    print(quest)
    write_msg(user_id, task, 'quest.json')


def check_answer(user_id, request):
    '''
    Checks if user message is the same as the right answer
    :param user_id:
    :param request:
    :return:
    '''
    return request.lower() == quest.iloc[int(get_user_data(user_id, 'step'))]['answer'].lower()


def check_end(user_id):
    '''
    Checks if user already completed the quest
    :param user_id:
    :return:
    '''
    step = get_user_data(user_id, 'step')
    if step == len(quest):
        return True
    return False


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            users = check_user(event.user_id)
            request = event.text

            if request in ('Меню', 'Назад') or request.lower().startswith('привет'):  # Calls usual menu
                users = change_user_data(event.user_id, 'bot_answers', 1)
                write_msg(event.user_id, 'Чего изволите?', 'default.json')

            elif request == 'Поговорить с человеком':  # Stops bot responses
                users = change_user_data(event.user_id, 'bot_answers', 0)
                write_msg(event.user_id, 'Мы ответим КТТС', 'menu_call.json')

            elif request in QUESTIONS.keys():  # For Ruslan
                write_msg(event.user_id, QUESTIONS[request])

            elif request.startswith('http'):
                get_id(request)

            elif get_user_data(event.user_id, 'bot_answers'):  # Usual response
                if request in ('Квест', 'Текущее задание', 'Следующее задание'):
                    if not check_subscription(event.user_id, GROUP_ID):  # Checking if user is subscribed
                        message = 'Чтобы выполнять квест, подпишись на нашу группу'
                        write_msg(event.user_id, message, 'default.json')
                    elif check_end(event.user_id):  # Check if quest is already passed
                        score = get_user_data(event.user_id, "score")
                        message = f'Ты уже выполнил наш квест \nТы набрал {score} баллов'
                        write_msg(event.user_id, message, 'default.json')
                    else:
                        send_task(event.user_id)  # Just sending the task

                elif request == 'Баллы квеста':  # Returns quest score
                    score = get_user_data(event.user_id, "score")
                    score = int(score) if int(score) == score else score
                    message = f'У тебя {score} баллов, шик'
                    write_msg(event.user_id, message, 'default.json')

                elif request == 'Задать вопросы':
                    write_msg(event.user_id, 'Что хочешь узнать?', 'questions1.json')

                elif request.startswith('Страница '):
                    num = request[-1]
                    write_msg(event.user_id, 'Что хочешь узнать?', f'questions{num}.json')

                elif check_answer(event.user_id, request):
                    score_delta = get_quest_data(get_user_data(event.user_id, 'step'), 'score')
                    users = increase_value(event.user_id, 'score', score_delta)

                    specials = {'15': 22}

                    if str(request) in specials:
                        users = change_user_data(event.user_id, 'step', specials[str(request)])
                    else:
                        users = increase_value(users, event.user_id, 'step', 1)

                    if check_end(event.user_id):
                        score = get_user_data(event.user_id, 'score')
                        write_msg(event.user_id, f'Красава, всё прошёл \nУ тебя {score} баллов', 'default.json')

                else:
                    write_msg(event.user_id, f'Иди на хуй со своим "{request}", сука!', 'default.json')
