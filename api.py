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


def send_task(user_id):
    '''
    Sends current quest task to the given user
    :param user_id:
    :return:
    '''
    step = get_user_data(user_id, 'step')
    task = get_quest_data(step, 'task')
    write_msg(event.user_id, task, 'quest.json')


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