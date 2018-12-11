from app import app, render_template, flash, redirect
from app.models import *
from app.forms import LoginForm, AccountForm, AddNewUserForm, DeleteUserForm
from flask import url_for
from flask_login import login_user, current_user, logout_user, login_required
from app import posts

@app.route('/home')
@app.route('/')
def home():
    users = Users.query.filter(Users.boss_id == None).all()
    # users = Users.query.order_by(Users.hierarchy).filter_by(boss_id=1).all()
    return render_template('home.html', users=users)# , users=users)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
            user = Users.query.filter_by(id=form.id.data).first()
            login_user(user, remember=True)
            flash('Вы вошли как {}'.format(user.name), 'success')
            return redirect(url_for('home'))
    return render_template('login.html', form=form)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user_pic = url_for('static', filename='pics/' + current_user.user_pic)
    all_posts = [post[0] for post in posts]
    post_names = [i for i in all_posts if i != current_user.post_name]
    acc_form = AccountForm(prefix='form1')
    new_user_form = AddNewUserForm(prefix='form2')
    delete_user_form = DeleteUserForm(prefix='form3')
    if acc_form.submit1.data and acc_form.validate_on_submit():
        print('1')
        flash('Сохранено', 'success')
        return redirect(url_for('account'))
    if new_user_form.submit2.data and new_user_form.validate_on_submit():
        print('2')
        flash('Пользователь добавлен', 'success')
        return redirect(url_for('account'))
    if delete_user_form.submit3.data and delete_user_form.validate_on_submit():
        print('3')
        flash('Пользователь удален', 'success')
        return redirect(url_for('account'))
    return render_template('account.html',
                           acc_form=acc_form,
                           posts=post_names,
                           user_pic=user_pic,
                           new_user_form=new_user_form,
                           all_posts=all_posts,
                           delete_user_form=delete_user_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/employers')
@login_required
def employers():
    all_users = Users.query.order_by(Users.id).all()
    return render_template('employers.html', users=all_users)

