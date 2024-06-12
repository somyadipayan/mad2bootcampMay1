from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text, DateTime
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
ma = Marshmallow()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'user'

    email = Column(Text, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    city = Column(Text)
    last_loggedin = Column(DateTime, nullable=False)

    def __init__(self, email, name, password, role, city, last_loggedin):
        self.email = email
        self.name = name
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.role = role
        self.city = city
        self.last_loggedin = last_loggedin


class UserSchema(ma.Schema):
    class Meta:
        fields = ('email', 'name', 'password', 'role', 'city', 'last_loggedin')

user_schema = UserSchema()
users_schema = UserSchema(many=True)