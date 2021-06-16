# Working with db
def check_user(user_id):
    '''
    Checks if user is in the BD
    If not, creates him there
    :param user_id:
    :return:
    '''
    global users

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


def get_quest_data(step_id, field):
    return quest.loc[step_id, field]