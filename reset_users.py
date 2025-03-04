from app import app, db
from models import User
from sqlalchemy.sql import text

with app.app_context():
    User.query.delete()
    db.session.execute(text('ALTER SEQUENCE user_id_seq RESTART WITH 1'))
    db.session.commit()
    next_id = db.session.execute(text('SELECT nextval(\'user_id_seq\')')).scalar()
    print(f"All users deleted successfully. Next ID will be: {next_id}")
from app import app, db
from models import User
from sqlalchemy.sql import text

with app.app_context():
    User.query.delete()
    db.session.execute(text('ALTER SEQUENCE user_id_seq RESTART WITH 1'))
    db.session.commit()
    next_id = db.session.execute(text('SELECT nextval(\'user_id_seq\')')).scalar()
    print(f"All users deleted successfully. Next ID will be: {next_id}")
