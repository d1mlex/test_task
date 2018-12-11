from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField
from wtforms.validators import InputRequired, ValidationError, Optional
from datetime import date
from app.models import Users
from flask_login import current_user
from app import app, db
from app import posts
from random import choice
import os

class LoginForm(FlaskForm):
    id = IntegerField('Код сотрудника:', validators=[InputRequired()])
    password = PasswordField('Пароль (password):',  validators=[InputRequired()])
    submit = SubmitField('Войти')

    def validate_id(self, id):
        if Users.query.filter_by(id=id.data).first():
            return True
        message = 'Такого пользователя нет'
        raise ValidationError(message)

    def validate_password(self, password):
        if password.data == 'password':
            return True
        message = 'Неправильный пароль (нужно ввести password)'
        raise ValidationError(message)






class AccountForm(FlaskForm):

    id = StringField('Ваш код')
    user_pic = FileField('Обновить фотографию', validators=[FileAllowed(['jpg', 'png'])])
    name = StringField('Ваше имя')
    post_name = StringField('Ваша должность')
    salary = IntegerField('Зарплата', validators=[Optional()])
    hire_date = DateField('Дата приема на работу', validators=[Optional()], format='%Y-%m-%d')
    boss_id = IntegerField('Начальник', validators=[Optional()])
    submit1 = SubmitField('submit')

    def validate_salary(self, salary):
        if salary.data:
            if 10000 > salary.data:
                message = 'Зарплата не может быть такой маленькой'
            elif 1200000 < salary.data:
                message = 'Слишком большая зарплата'
            else:
                current_user.salary = salary.data
                db.session.commit()
                return True
            raise ValidationError(message)

    def validate_hire_date(self, hire_date):
        if hire_date.data:
            if hire_date.data < date(2000, 2, 1):
                message = 'Слишком рано'
            elif hire_date.data > date.today():
                message = 'Дата еще не наступила'
            else:
                current_user.hire_date = hire_date.data
                db.session.commit()
                return True
            return ValidationError(message)

    def validate(self):
        errors = ()
        if not FlaskForm.validate(self):   # запускаем стандартный validate() и собираем ошибки в errors
            errors = FlaskForm.errors
        if self.name.data:       # Добавляем имя, если введено новое
            current_user.name = self.name.data
            db.session.commit()
        if self.boss_id.data:   # проверяем код начальника, если есть
            if not Users.query.filter_by(id=self.boss_id.data).first():
                message = 'Такого сотрудника нет'
                self.boss_id.errors += (message,)
            else:
                post_level = Users.query.filter_by(post_name=current_user.post_name).first().level()
                boss_ids = [user.id for user in Users.query.all() if user.level() == post_level - 1]
                if self.boss_id.data not in boss_ids:
                    message = 'Данный сотрудник не подходит по должности'
                    self.boss_id.errors += (message,)
            if self.boss_id.errors:
                return False
            current_user.boss_id = self.boss_id.data
            db.session.commit()

        if errors:     # Если были ошибки в стандартном validate()
            return False
        if self.post_name.data:    # Добавляем должность, назначаем нового начальника и перераспределяем подчиненных
            hierarchy_level = [post[0] for post in posts].index(self.post_name.data)
            if hierarchy_level == 0:   # Если выбрали ген. директора
                current_user.boss_id = None
                db.session.commit()
                current_user.save(add=False)
            else:     # Случайно выбираем босса в зависимости от новой должности
                new_boss_id = choice([boss.id for boss in Users.query.all() if boss.level() == hierarchy_level - 1])
                current_user.boss_id = new_boss_id
                db.session.commit()
                current_user.save(add=False)
            if current_user.manages.first():   # Если были подчиненные
                employee_level = current_user.manages.first().level()   # Уровень сотрудника
                possible_new_bosses = [boss.id for boss in Users.query.all() if boss.level() == employee_level - 1]
                for employee in current_user.manages.all():
                    employee.boss_id = choice(possible_new_bosses)
                    employee.save(add=False)
            current_user.post_name = self.post_name.data
            db.session.commit()
        if self.user_pic.data:
            picture_file = save_picture(self.user_pic.data)
            current_user.user_pic = picture_file
            db.session.commit()
        return True


def save_picture(user_pic):
    _, f_ext = os.path.splitext(user_pic.filename)
    pic_filename = str(current_user.id) + f_ext
    picture_path = os.path.join(app.root_path, 'static/pics', pic_filename)
    user_pic.save(picture_path)

    return pic_filename


class AddNewUserForm(FlaskForm):
    name = StringField('Имя*', validators=[InputRequired()])
    post_name = StringField('Должность*', validators=[InputRequired()])
    salary = IntegerField('Зарплата*', validators=[InputRequired()])
    boss_id = IntegerField('Код начальника', validators=[Optional()])
    user_pic = FileField('Загрузить фото', validators=[FileAllowed(['jpg', 'png'])])
    submit2 = SubmitField('submit2')

    def validate(self):
        errors = ()
        if not FlaskForm.validate(self):
            errors = FlaskForm.errors
        if self.boss_id.data:
            if not Users.query.filter_by(id=self.boss_id.data).first():
                message = 'Такого сотрудника нет'
                self.boss_id.errors += (message,)
            else:
                hierarchy_level = [post[0] for post in posts].index(self.post_name.data)
                boss_ids = [boss.id for boss in Users.query.all() if boss.level() == hierarchy_level - 1]
                if self.boss_id.data not in boss_ids:
                    message = 'Нельзя выбрать данный код'
                    self.boss_id.errors += (message,)
            if self.boss_id.errors:
                return False
        print(errors)
        if errors:  # Если были ошибки в стандартном validate()
            return False
        else:
            name = self.name.data
            post_name = self.post_name.data
            salary = self.salary.data
            if self.boss_id.data:
                boss_id = self.boss_id.data
            else:
                hierarchy_level = [post[0] for post in posts].index(self.post_name.data)
                if hierarchy_level:
                    boss_id = choice([boss.id for boss in Users.query.all() if boss.level() == hierarchy_level - 1])
                else:
                    boss_id = None
            if self.user_pic.data:
                user_pic = save_picture(self.user_pic.data)
            else:
                user_pic = 'default.jpg'
            hire_date = date.today()
            new_user = Users(name=name,
                             post_name=post_name,
                             salary=salary,
                             hire_date=hire_date,
                             boss_id=boss_id,
                             user_pic=user_pic)
            new_user.save()
            return True


class DeleteUserForm(FlaskForm):
    id = IntegerField('Код сотрудника', validators=[InputRequired()])
    submit3 = SubmitField('submit3')

    def validate_id(self, id):
        if Users.query.filter_by(id=id.data).first():
            Users.query.filter_by(id=id.data).delete()
            db.session.commit()
            return True
        message = 'Такого пользователя нет'
        raise ValidationError(message)
