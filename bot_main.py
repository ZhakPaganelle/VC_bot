import pandas
import vk_api
from random import randint
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Constants and preparations
token = open('api_key.txt').read()
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)

users = pandas.read_csv('users.csv', index_col='user_id')
# DB structure: user_id, bot_answers, score, step, way
questions = {'Как жизнь?': ')', 'Го по пиву?': 'Го!'}

print(users)


# Working with db
def check_user(user_id):
    global users

    if user_id not in set(users.index):
        new_user = [1, 0, 0, 'course']
        # users = users.append(pandas.Series(new_user, name=user_id))
        users.loc[user_id, :] = new_user
        print(users)
        users.to_csv('users.csv', encoding='utf-8')

    return users


def get_user_data(user_id, field):
    return users.loc[user_id, field]


def change_user_data(user_id, field, value):
    users.loc[user_id, field] = value
    users.to_csv('users.csv', encoding='utf-8')


def increase_score(user_id, delta):
    current_score = get_user_data(user_id, 'score')
    new_score = current_score + delta
    change_user_data(user_id, 'score', new_score)


# Working with vk api
def write_msg(user_id, message, keyboard_file='empty.json'):
    keyboard = open(f'keyboards/{keyboard_file}', encoding='utf-8').read()
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'keyboard': keyboard, 'random_id': randint(10**5, 10**6)})


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
                write_msg(event.user_id, questions[request], 'questions.json')

            elif get_user_data(event.user_id, 'bot_answers'):  # Usual response

                if request == 'Баллы квеста':
                    score = get_user_data(event.user_id, "score")
                    score = int(score) if int(score) == score else score
                    message = f'У тебя {score} баллов, шик'
                    write_msg(event.user_id, message, 'default.json')
                elif request == 'Задать вопросы':
                    write_msg(event.user_id, 'Что хочешь узнать?', 'questions.json')
                else:
                    write_msg(event.user_id, f'Иди на хуй со своим "{request}", сука!', 'default.json')
