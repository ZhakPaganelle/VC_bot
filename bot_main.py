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

quest = pandas.read_csv('quest.csv', index_col='step_id', sep=';')
# DB structure: step_id, task, answer, score

admins = pandas.read_csv('admins.csv', index_col='admin_id')
# DB structure: admin_id, last checked user

subscribe_message = '''Как я вижу, ты заинтересовался доброквестом, но, видимо, ты не подписан на нашу группу вк… У нас не получится наладить контакт, если ты не будешь подписан…
Возвращайся когда выполнишь это задание!
'''


# Working with db
def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


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
        users.to_csv('users.csv', encoding='utf-8')

    return users


def get_data(db, row, field):
    '''
    Returns field in given row

    :param db:
    :param row:
    :param field:
    :return:
    '''

    return db.loc[row, field]


def change_data(db, row, field, value):
    '''
    Changes field value to value param
    :param db:
    :param row:
    :param field:
    :param value:
    :return:
    '''
    db.loc[row, field] = value
    sep = ';' if db is quest else ','
    db.to_csv(f'{namestr(db, globals())[0]}.csv', encoding='utf-8', sep=sep)

    return db


def increase_value(db, row, field, delta):
    '''
    Increases field param by delta
    :param field:
    :param delta:
    :return:
    '''
    current_value = get_data(db, row, field)
    new_value = current_value + delta
    change_data(db, row, field, new_value)

    return users


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
    data = vk.method('users.get', {'user_ids': link, 'fields': 'uid'})

    return data[0]['id']


def send_task(user_id):
    '''
    Sends current quest task to the given user
    :param user_id:
    :return:
    '''
    step = get_data(users, user_id, 'step')
    task = get_data(quest, step, 'task').replace('!?!', '\n')
    write_msg(user_id, task, 'quest.json')


def check_answer(user_id, request):
    '''
    Checks if user message is the same as the right answer
    :param user_id:
    :param request:
    :return:
    '''
    return request.lower() == quest.iloc[int(get_data(users, user_id, 'step'))]['answer'].lower()


def check_end(user_id):
    '''
    Checks if user already completed the quest
    :param user_id:
    :return:
    '''
    step = get_data(users, user_id, 'step')
    if step == len(quest):
        return True
    return False


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            users = check_user(event.user_id)
            request = event.text

            if str(event.user_id) in ADMIN_IDS and request.startswith('http') or len(request) == 1:
                # try:  # Uncomment when deploy
                if request.startswith('http'):
                    user_id = get_id(request)
                    change_data(admins, event.user_id, 'last_user_checked', user_id)

                    user_step = get_data(users, user_id, 'step'),
                    if (value := int(get_data(quest, user_step, 'score'))) < 10:
                        increase_value(users, user_id, 'step', 1)
                        increase_value(users, user_id, 'score', value)

                        if not check_end(user_id):
                            write_msg(user_id, 'Красава')
                            user_step = get_data(users, user_id, 'step')
                            send_task(user_id)
                        else:
                            score = get_data(users, event.user_id, 'score')
                            write_msg(event.user_id, f'Красава, всё пройдено \nУ тебя {score} баллов', 'default.json')
                    else:
                        value = str(value)
                        write_msg(event.user_id, 'Сколько начислять?', f'{value}.json')

                elif len(request) == 1:
                    user_id = get_data(admins, event.user_id, 'last_user_checked')
                    increase_value(users, user_id, 'step', 1)
                    increase_value(users, user_id, 'score', int(request))
                    if not check_end(user_id):
                        write_msg(user_id, 'Красава')
                        user_step = get_data(users, user_id, 'step')
                        send_task(user_id)
                    else:
                        score = get_data(users, event.user_id, 'score')
                        score = int(score) if int(score) == score else score
                        write_msg(event.user_id, f'Красава, всё пройдено \nУ тебя {score} баллов', 'default.json')
                # except:
                #     pass

            elif request in ('Меню', 'Назад') or request.lower().startswith('привет'):  # Calls usual menu
                users = change_data(users, event.user_id, 'bot_answers', 1)
                write_msg(event.user_id, 'Чего изволите?', 'default.json')

            elif request == 'Поговорить с человеком':  # Stops bot responses
                users = change_data(users, event.user_id, 'bot_answers', 0)
                write_msg(event.user_id, 'Мы ответим КТТС', 'menu_call.json')

            elif request in QUESTIONS.keys():  # For Ruslan
                write_msg(event.user_id, QUESTIONS[request])

            elif get_data(users, event.user_id, 'bot_answers'):  # Usual response
                if request in ('Квест', 'Текущее задание', 'Следующее задание'):
                    if not check_subscription(event.user_id, GROUP_ID):  # Checking if user is subscribed
                        write_msg(event.user_id, subscribe_message, 'default.json')
                    elif check_end(event.user_id):  # Check if quest is already passed
                        score = get_data(users, event.user_id, "score")
                        score = int(score) if int(score) == score else score
                        message = f'Ты уже выполнил наш квест \nТы набрал {score} баллов'
                        write_msg(event.user_id, message, 'default.json')
                    else:
                        send_task(event.user_id)  # Just sending the task

                elif request == 'Баллы квеста':  # Returns quest score
                    score = get_data(users, event.user_id, "score")
                    score = int(score) if int(score) == score else score
                    message = f'У тебя {score} баллов, шик'
                    write_msg(event.user_id, message, 'default.json')

                elif request == 'Задать вопросы':
                    write_msg(event.user_id, 'Что хочешь узнать?', 'questions1.json')

                elif request.startswith('Страница '):
                    num = request[-1]
                    write_msg(event.user_id, 'Что хочешь узнать?', f'questions{num}.json')

                # elif check_answer(event.user_id, request):
                #     score_delta = get_data(quest, get_data(users, event.user_id, 'step'), 'score')
                #     users = increase_value(users, event.user_id, 'score', score_delta)
                #
                #     specials = {'15': 22}
                #
                #     if str(request) in specials:
                #         users = change_data(users, event.user_id, 'step', specials[str(request)])
                #     else:
                #         users = increase_value(users, event.user_id, 'step', 1)
                #
                #     if check_end(event.user_id):
                #         score = get_data(users, event.user_id, 'score')
                #         write_msg(event.user_id, f'Красава, всё прошёл \nУ тебя {score} баллов', 'default.json')
                #
                # else:
                #     write_msg(event.user_id, f'Иди на хуй со своим "{request}", сука!', 'default.json')
