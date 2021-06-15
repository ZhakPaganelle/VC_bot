import pandas
import vk_api
from random import randint
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Constants and preparations
token = open('api_key.txt').read()
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
group_id = '194815411'

users = pandas.read_csv('users.csv', index_col='user_id')
# DB structure: user_id, bot_answers, score, step, way

quest = pandas.read_csv('quest.csv', index_col='step_id')
# DB structure: step_id, task, answer, score

questions = {'Как жизнь?': ')', 'Го по пиву?': 'Го!'}

print(users)


# Working with db
def check_user(user_id):
    global users

    if user_id not in set(users.index):
        new_user = [1, 0, 0, 'course']
        users.loc[user_id, :] = new_user
        print(users)
        users.to_csv('users.csv', encoding='utf-8')

    return users


def get_user_data(user_id, field):
    return users.loc[user_id, field]


def change_user_data(user_id, field, value):
    users.loc[user_id, field] = value
    users.to_csv('users.csv', encoding='utf-8')


def increase_value(user_id, field, delta):
    current_value = get_user_data(user_id, field)
    new_value = current_value + delta
    change_user_data(user_id, field, new_value)


def get_quest_data(step_id, field):
    return quest.loc[step_id, field]


# Working with vk api
def write_msg(user_id, message, keyboard_file='empty.json'):
    keyboard = open(f'keyboards/{keyboard_file}', encoding='utf-8').read()
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard, 'random_id': randint(10**5, 10**6)})


def check_subscription(user_id, group_id):
    return vk.method('groups.isMember', {'group_id': group_id, 'user_id': user_id})


def send_task(user_id):
    step = get_user_data(user_id, 'step')
    task = get_quest_data(step, 'task')
    write_msg(event.user_id, task, 'quest.json')


def check_answer(user_id, request):
    return request.lower() == quest.iloc[int(get_user_data(user_id, 'step'))]['answer'].lower()


def check_end(user_id):
    step = get_user_data(user_id, 'step')
    if step == len(quest):
        return True
    return False


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            users = check_user(event.user_id)
            request = event.text

            if request in ('Меню', 'Назад', 'Привет'):  # Calls usual menu
                change_user_data(event.user_id, 'bot_answers', 1)
                write_msg(event.user_id, 'Чего изволите?', 'default.json')

            elif request == 'Поговорить с человеком':  # Stops bot responses
                change_user_data(event.user_id, 'bot_answers', 0)
                write_msg(event.user_id, 'Мы ответим КТТС', 'menu_call.json')

            elif request in questions:  # For Ruslan
                write_msg(event.user_id, questions[request], 'questions1.json')

            elif get_user_data(event.user_id, 'bot_answers'):  # Usual response
                if request in ('Квест', 'Текущее задание', 'Следующее задание'):
                    if not check_subscription(event.user_id, group_id):
                        message = 'Чтобы выполнять квест, подпишись на нашу группу'
                        write_msg(event.user_id, message, 'default.json')
                    elif check_end(event.user_id):
                        score = get_user_data(event.user_id, "score")
                        message = f'Ты уже выполнил наш квест \nТы набрал {score} баллов'
                        write_msg(event.user_id, message, 'default.json')
                    else:
                        send_task(event.user_id)

                elif request == 'Баллы квеста':
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
                    increase_value(event.user_id, 'score', get_quest_data(get_user_data(event.user_id, 'step'), 'score'))

                    specials = {'15': 22}

                    if str(request) in specials:
                        change_user_data(event.user_id, 'step', specials[str(request)])
                    else:
                        increase_value(event.user_id, 'step', 1)

                    if check_end(event.user_id):
                        write_msg(event.user_id, 'Красава, всё прошёл', 'default.json')

                else:
                    write_msg(event.user_id, f'Иди на хуй со своим "{request}", сука!', 'default.json')
