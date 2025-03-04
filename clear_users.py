from extensions import app, db
from models import User

with app.app_context():
    db.session.query(User).delete()
    db.session.commit()
    print("User table cleared successfully")
