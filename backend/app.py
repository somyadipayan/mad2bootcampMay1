from flask import Flask, request, jsonify
from config import Config
from models import *
from datetime import datetime
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, unset_jwt_cookies


app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)
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

#LOGIN API
@app.route("/login", methods= ["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    if not email or not password:
        return {"error": "Email and password are required"}, 400
    
    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return {"error": "Invalid Credentials"}, 401
    
    access_token = create_access_token(identity={
        "email": user.email,
        "name": user.name,
        "role": user.role
    })

    return jsonify({"access_token": access_token, "message": "Login successful"}), 200

# THIS ROUTE TO BE ACCESSIBLE ONLY BY LOGGED IN USERS
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    print(current_user["role"])
    return jsonify(logged_in_as=current_user), 200


@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({'message': 'logout successful'})
    unset_jwt_cookies(response)
    return response

@app.route("/getuserinfo", methods= ["GET"])
@jwt_required()
def get_userinfo():
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user["email"]).first()
    user_data = user_schema.dump(user)
    return jsonify(user_data), 200

if __name__ == "__main__":
    app.run(debug=True)