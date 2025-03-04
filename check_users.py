from app import app, db
from models import User

with app.app_context():
    user_count = User.query.count()
    users = User.query.all()
    print(f"Total users: {user_count}")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")
