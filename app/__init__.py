from flask import Flask, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

posts = [['Генеральный директор', 1000000],
         ['Директор', 200000],
         ['Начальник отдела', 60000],
         ['Тимлид', 40000],
         ['Работник', 20000]]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f9adbde9469176badf2962d240bd6f6b'

db_credentials = <postgres credentials>
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres+psycopg2://postgres:' + db_credentials

db = SQLAlchemy(app)
login_manager = LoginManager(app)

migrate = Migrate(app, db)

from app import models, routes
