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

    user.last_loggedin = datetime.now()
    db.session.commit()

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

# CRUD ON CATEGORIES

# Creating a Category
@app.route("/category", methods= ["POST"])
@jwt_required()
def create_category():
    this_user = get_jwt_identity()
    # Only for manager and admin
    if this_user["role"] == "user":
        return {"error": "Unauthorized"}, 401
    
    data = request.json
    name = data["name"]
    if not name:
        return {"error": "Name is required"}, 400
    
    creator_email = this_user["email"]
    if this_user["role"] == "admin":
        verified = True
    else:
        verified = False

    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return {"error": "Category already exists"}, 409
    new_category = Category(name, creator_email, verified)
    try: 
        db.session.add(new_category)
        db.session.commit()
        if this_user["role"] == "admin":
            return {"message": "Category created successfully"}, 201
        return {"message": "Category creation application Submitted Successfully"}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to create category: {str(e)}"}, 500

# GET ALL CATEGORIES
@app.route("/categories", methods= ["GET"])
def get_categories():
    categories = Category.query.all()
    categories_data = categories_schema.dump(categories)
    return jsonify(categories_data), 200

# GET SINGLE CATEGORY by ID
@app.route("/category/<int:id>", methods= ["GET"])
def get_category(id):
    category = Category.query.filter_by(id=id).first() 
    if not category:
        return {"error": "Category not found"}, 404
    category_data = category_schema.dump(category)
    return jsonify(category_data), 200

# UPDATE CATEGORY
@app.route("/category/<int:id>", methods= ["PUT"])
@jwt_required()
def update_category(id):
    this_user = get_jwt_identity()

    if this_user["role"] == "user":
        return {"error": "Unauthorized"}, 401
    
    data = request.json
    name = data["name"]
    if not name:
        return {"error": "Name is required"}, 400
    category = Category.query.get(id)
    if not category:
        return {"error": "Category not found"}, 404
    existing_category = Category.query.filter_by(name=name).first()

    if existing_category and existing_category.id != id:
        return {"error": "Category already exists"}, 409
    
    category.name = name
    try: 
        db.session.commit()
        return {"message": "Category updated successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to update category: {str(e)}"}, 500

# DELETE CATEGORY by ID
@app.route("/category/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_category(id):
    this_user = get_jwt_identity()

    if this_user["role"] != "admin":
        return {"error": "Unauthorized"}, 401
    
    category = Category.query.get(id)
    if not category:
        return {"error": "Category not found"}, 404
    
    try:
        db.session.delete(category)
        db.session.commit()
        return {"message": "Category deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to delete category: {str(e)}"}, 500

if __name__ == "__main__":
    app.run(debug=True)