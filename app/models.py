from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    _N = 6       # количество знаков в максимальном числе сотрудников

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_pic = db.Column(db.String, default='default.jpg')
    post_name = db.Column(db.String)
    salary = db.Column(db.Integer)
    hire_date = db.Column(db.Date)
    boss_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    hierarchy = db.Column(db.Text, index=True)
    manages = db.relationship('Users',
                              backref=db.backref('boss', remote_side=[id]),
                              lazy='dynamic')

    def save(self, add=True):
        if add:
            db.session.add(self)
            db.session.commit()
        if self.boss_id:
            prefix = self.boss.hierarchy + '.' if self.boss else ''
        else:
            prefix = ''  # Для ген. директора
        self.hierarchy = prefix + '{:0{}d}'.format(self.id, self._N)
        db.session.commit()

    def level(self):
        return len(self.hierarchy) // self._N - 1
