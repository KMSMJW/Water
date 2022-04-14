from app import create_app
from database import db

with create_app().app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()