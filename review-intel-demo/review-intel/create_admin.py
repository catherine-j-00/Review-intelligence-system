import getpass
import sys
from backend.app import create_app
from backend.database.db import db
from backend.database.models import User

app = create_app()
with app.app_context():
    username = input('Admin username: ').strip()
    password = getpass.getpass('Password (min 10 characters): ')
    if len(password) < 10:
        sys.exit('Password too short')
    user = User.query.filter_by(username=username).first() or User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print('Admin saved')
