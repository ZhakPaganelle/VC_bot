import random

import pandas as pd


class Admin:
    def __init__(self, admin_id, last_checked):
        self.admin_id = admin_id
        self.last_checked = last_checked

    def change_score(self, score=1, user=None):
        if not user:
            user = self.last_checked
        if user.is_numeric():
            user = str(int(user))
        users_dict[user].change_score(score)

    def change_step(self, step_delta=1, user=None):
        if not user:
            user = self.last_checked
        if user.is_numeric():
            user = str(int(user))
        users_dict[user].change_step(step_delta)

    def change_last_checked(self, new_user):
        self.last_checked = new_user
        update_db(admins, self.admin_id, 'last_user_checked', new_user)


def renew_admins():
    global admins_dict, admins

    admins_dict = {}
    admins = pd.read_csv('admins.csv', index_col='admin_id')
    for admin_id, admin in admins.iterrows():
        admins_dict[admin_id] = Admin(admin_id, admin['last_user_checked'])

    return admins, admins_dict


class User:
    def __init__(self, user_id, score=0, step=0, likes=0):
        self.user_id = user_id
        self.score = int(score)
        self.step = int(step)
        self.likes = int(likes)

    def change_score(self, delta):
        self.score += delta
        update_db(users, self.user_id, 'score', self.score)

    def change_step(self, new_step=None):
        if new_step:
            self.step = new_step
        elif self.step == 7:
            self.step = random.randint(8, 10)
        elif self.step in range(8, 11):
            self.step = 11
        else:
            self.step += 1
        print(self.step)
        update_db(users, self.user_id, 'step', self.step)

    def change_likes(self):
        self.likes += 1
        update_db(users, self.user_id, 'likes', self.likes)


def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]


def renew_users():
    global users_dict, users

    users_dict = {}
    users = pd.read_csv('users.csv', index_col='user_id')
    for user_id, user in users.iterrows():
        users_dict[user_id] = User(user_id, user['score'], user['step'], user['likes'])

    return users, users_dict


def update_db(db, row, field, value):
    # print(row, field)
    db.loc[row, field] = value
    db.to_csv(f'{namestr(db, globals())[0]}.csv')


def check_user(user_id):
    global users, users_dict

    if user_id not in users_dict.keys():
        users.loc[user_id, :] = [0, 0, 0]
        users.to_csv('users.csv', encoding='utf-8')
        users, users_dict = renew_users()

    return users, users_dict


users, users_dict = renew_users()

# list(users_dict.values())[1].change_step()

# print(users.head())

admins, admins_dict = renew_admins()
# admins_dict[185510152].change_last_checked(192)
# print(admins_dict[185510152].last_checked)
