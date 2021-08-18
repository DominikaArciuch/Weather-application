from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
app.secret_key = "super secret key"


class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)


SQLALCHEMY_TRACK_MODIFICATIONS = False
db.create_all()
