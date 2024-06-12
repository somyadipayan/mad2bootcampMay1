from flask import Flask, request
from config import Config
from models import *
from datetime import datetime
from flask_cors import CORS


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
ma.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    db.create_all()

CORS(app, supports_credentials=True)

@app.route("/create-admin", methods= ["POST"])
def create_admin():
    existing_admin = User.query.filter_by(role="admin").first()

    if existing_admin:
        return {"error": "Admin already exists"}, 409

    email = "admin@store.com"
    name = "admin"
    password = "1"
    role = "admin"
    city = "Chennai"

    last_loggedin = datetime.now()

    if not email or not name or not password or not role:
        return {"error": "All fields are required"}, 400

    try:
        new_admin = User(email, name, password, role, city, last_loggedin)
        db.session.add(new_admin)
        db.session.commit()
        return {"message": "Admin created successfully"}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to create admin: {str(e)}"}, 500

@app.route("/", methods= ["GET"])
def home():
    return "Hello World"

@app.route("/register", methods= ["POST"])
def register():
    data = request.json
    email = data["email"]
    name = data["name"]
    password = data["password"]
    role = data["role"]
    city = data["city"]

    last_loggedin = datetime.now()

    if not email or not name or not password or not role:
        return {"error": "All fields are required"}, 400
    
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {"error": "User already exists"}, 409

    new_user = User(email, name, password, role, city, last_loggedin)

    try: 
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created successfully"}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to create user: {str(e)}"}, 500


if __name__ == "__main__":
    app.run(debug=True)