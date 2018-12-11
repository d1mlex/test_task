from app.models import *
import csv
from random import choice, choices, randint
from datetime import date
from app import posts

# =========== Генерирование должностей =========== #

Users.__table__.drop(db.engine)
print('Deleting Users table')
db.metadata.create_all(db.engine, [Users.__table__])
print('Creating new Users table')
db.session.commit()

# =========== Генерирование спика имен =========== #

with open('names.csv', encoding='cp1251', newline='') as f:
    data = csv.reader(f)
    names_dict = dict(data)

with open('surnames.csv', encoding='cp1251', newline='') as f:
    data = csv.reader(f)
    surnames_dict = dict(data)

surnames = {}
names = {}
for k, v in names_dict.items():             # разворачиваем dict -> {'m':[список имен]}
    names.setdefault(v, []).append(k)
for k, v in surnames_dict.items():
    surnames.setdefault(v, []).append(k)

first_hire = date(2000, 2, 1).toordinal()
last_hire = date.today().toordinal()
users_count = 50000   # Можно ввести желаемое значение сотрудников
users = []
post_id = 0
next_post = 1
employee_on_post = 1
employee_on_prev_post = 0
first_boss_id = last_boss_id = 1

for i in range(1, users_count+1):
    id = i
    gender = choices(['m', 'f'], [0.7, 0.3])[0]
    user_name = choice(surnames[gender]) + ' ' + choice(names[gender])
    post_name = posts[post_id][0]
    salary = int(posts[post_id][1] * (1 + randint(-20,20)/100))
    hire_date = date.fromordinal(randint(first_hire, last_hire))
    boss_id = randint(first_boss_id, last_boss_id) if id != 1 else None
    user = Users(name=user_name,
                 post_name=post_name,
                 salary=salary,
                 hire_date=hire_date,
                 boss_id=boss_id)
    user.save()
    if i == next_post:
        post_id += 1
        first_boss_id = next_post - employee_on_post + 1
        last_boss_id = id
        employee_on_post *= 15
        next_post += employee_on_post

db.session.commit()









