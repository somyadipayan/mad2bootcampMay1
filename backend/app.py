from flask import Flask, request, jsonify, send_from_directory, send_file
from config import Config
from models import *
from datetime import datetime, timedelta
from flask_cors import CORS
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, unset_jwt_cookies
from werkzeug.utils import secure_filename
import os
import io
import matplotlib.pyplot as plt
import workers, task
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)

celery = workers.celery
celery.conf.update(
    broker_url=app.config['CELERY_BROKER_URL'],
    result_backend=app.config['CELERY_RESULT_BACKEND']
)

celery.Task = workers.ContextTask
app.app_context().push()
jwt = JWTManager(app)
mail = Mail(app)
db.init_app(app)
ma.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
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
    # triggering task "multiply" from task.py
    task.multiply.delay(3, 4)
    task.add.delay()
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

# CRUD ON PRODUCTS
@app.route("/category/<int:id>/product", methods= ["POST"])
@jwt_required()
def create_product(id):
    this_user = get_jwt_identity()

    if this_user["role"] == "user":
        return {"error": "Unauthorized"}, 401
    
    data = request.json
    name = data["name"]
    unit = data["unit"]
    rateperunit = data["rateperunit"]
    quantity = data["quantity"]

    if not name or not unit or not rateperunit or not quantity:
        return {"error": "All fields are required"}, 400
    
    category = Category.query.get(id)
    if not category:
        return {"error": "Category not found"}, 404

    new_product = Product(
        name=name, 
        category_id=category.id,
        unit = unit,
        rateperunit= rateperunit,
        quantity = quantity,
        creator_email = this_user["email"])
    
    try: 
        db.session.add(new_product)
        db.session.commit()
        return {"message": "Product created successfully"}, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to create product: {str(e)}"}, 500

# GET ALL PRODUCTS
@app.route("/products", methods= ["GET"])
def get_all_products():
    products = Product.query.all()
    products_data = products_schema.dump(products)
    return jsonify(products_data), 200

# GET SINGLE PRODUCT by ID
@app.route("/product/<int:id>", methods= ["GET"])
def get_product(id):
    product = Product.query.filter_by(id=id).first() 
    if not product:
        return {"error": "Product not found"}, 404
    product_data = product_schema.dump(product)
    return jsonify(product_data), 200

# UPDATE PRODUCT
@app.route("/product/<int:id>", methods= ["PUT"])
@jwt_required()
def update_product(id):
    this_user = get_jwt_identity()

    if this_user["role"] == "user":
        return {"error": "Unauthorized"}, 401
    
    data = request.json
    name = data["name"]
    unit = data["unit"]
    rateperunit = data["rateperunit"]
    quantity = data["quantity"]
    category_id = data["category_id"]

    if not name or not unit or not rateperunit or not quantity or not category_id:
        return {"error": "All fields are required"}, 400
    
    product = Product.query.get(id)
    if not product:
        return {"error": "Product not found"}, 404
    
    product.name = name
    product.unit = unit
    product.rateperunit = rateperunit
    product.quantity = quantity
    product.category_id = category_id
    try: 
        db.session.commit()
        return {"message": "Product updated successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to update product: {str(e)}"}, 500

# DELETE PRODUCT by ID
@app.route("/product/<int:id>", methods= ["DELETE"])
@jwt_required()
def delete_product(id):
    this_user = get_jwt_identity()

    if this_user["role"] == "user":
        return {"error": "Unauthorized"}, 401
    
    product = Product.query.get(id)
    if not product:
        return {"error": "Product not found"}, 404
    
    try:
        db.session.delete(product)
        db.session.commit()
        return {"message": "Product deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to delete product: {str(e)}"}, 500

@app.route("/add-to-cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    current_user = get_jwt_identity()
    if current_user["role"] != "user":
        return {"message": "Unauthorized"}, 401
    data = request.json
    product_id = data["product_id"]
    quantity = request.json.get("quantity", 1)

    if quantity < 1:
        return {"error": "Quantity must be greater than 0"}, 400

    product = Product.query.get(product_id)
    if not product:
        return {"error": "Product not found"}, 404

    if quantity > product.quantity:
        return {"error": "Insufficient stock"}, 400

    user_cart = ShoppingCart.query.filter_by(user_email=current_user["email"]).first()
    if not user_cart:
        user_cart = ShoppingCart(user_email=current_user["email"])
        try:
            db.session.add(user_cart)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": f"Failed to create cart: {str(e)}"}, 500

    cart_item = CartItems.query.filter_by(shoppingcart_id=user_cart.id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItems(shoppingcart_id=user_cart.id, product_id=product_id, quantity=quantity)
    try:
        db.session.add(cart_item)
        db.session.commit()
        return {"message": "Product added to cart successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to add product to cart: {str(e)}"}, 500

@app.route("/view-cart", methods=["GET"])
@jwt_required()
def view_cart():
    current_user = get_jwt_identity()
    if current_user["role"] != "user":
        return {"error": "Unauthorized"}, 401
    user_cart = ShoppingCart.query.filter_by(user_email=current_user["email"]).first()
    if not user_cart:
        return {"message": "Cart is Empty"}, 200
    cart_items = CartItems.query.filter_by(shoppingcart_id=user_cart.id).all()
    cart_items_data = []
    for item in cart_items:
        cart_items_data.append({
            'cart_id': item.id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'product_name': item.product.name,
            'product_unit': item.product.unit,
            'product_rateperunit': item.product.rateperunit,
            'total_price': item.product.rateperunit * item.quantity
        })
    return jsonify({"cart": cart_items_data}), 200

@app.route("/update-cart", methods=["PUT"])
@jwt_required()
def update_cart():
    current_user = get_jwt_identity()
    if current_user["role"] != "user":
        return {"error": "Unauthorized"}, 401
    
    data = request.json
    cart_item_id = data.get("cart_item_id")
    new_quantity = data.get("quantity")

    if new_quantity < 1:
        return {"error": "Quantity must be greater than 0"}, 400
    
    cart_item = CartItems.query.filter_by(id=cart_item_id).first()
    if not cart_item:
        return {"error": "Cart item not found"}, 404
    
    user_cart = ShoppingCart.query.filter_by(id=cart_item.shoppingcart_id, user_email=current_user["email"]).first()
    if not user_cart:
        return {"error": "Unauthorized to update this cart item"}, 401
    
    if new_quantity > cart_item.product.quantity:
        return {"error": "Insufficient stock"}, 400
    
    cart_item.quantity = new_quantity

    try:
        db.session.commit()
        return {"message": "Cart item updated successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to update cart item: {str(e)}"}, 500

@app.route("/delete-from-cart/<int:cart_item_id>", methods=["DELETE"])
@jwt_required()
def delete_from_cart(cart_item_id):
    current_user = get_jwt_identity()
    if current_user["role"] != "user":
        return {"error": "Unauthorized"}, 401

    cart_item = CartItems.query.filter_by(id=cart_item_id).first()
    if not cart_item:
        return {"error": "Cart item not found"}, 404
    
    user_cart = ShoppingCart.query.filter_by(id=cart_item.shoppingcart_id, user_email=current_user["email"]).first()
    if not user_cart:
        return {"error": "Unauthorized to delete this cart item"}, 401
    
    try:
        db.session.delete(cart_item)
        db.session.commit()
        return {"message": "Cart item deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to delete cart item: {str(e)}"}, 500


@app.route('/verify-category/<int:id>', methods=['POST'])
@jwt_required()
def verify_category(id):
    current_user = get_jwt_identity()
    if current_user["role"] != "admin":
        return {"error": "Unauthorized"}, 401
    category = Category.query.get(id)
    if not category:
        return {"error": "Category not found"}, 404
    category.verified = True
    try:
        db.session.commit()
        return {"message": "Category verified successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to verify category: {str(e)}"}, 500
    
# ORDERS

@app.route("/place-order", methods=["POST"])
@jwt_required()
def place_order():
    current_user = get_jwt_identity() 
    user_cart = ShoppingCart.query.filter_by(user_email=current_user["email"]).first()
    if not user_cart or not user_cart.items:
        return {"message": "Cart is Empty"}, 200
    
    total_amount = 0
    order_items = []

    for item in user_cart.items:
        if item.quantity > item.product.quantity:
            return {"error": "Insufficient stock"}, 400
        total_amount += item.product.rateperunit * item.quantity
        order_item = OrderItems(
            product_id = item.product_id,
            quantity = item.quantity
                                )
        order_items.append(order_item)
        product = Product.query.filter_by(id=item.product_id).first()
        product.quantity -= item.quantity

    new_order = Order(
        user_email = current_user["email"],
        total_amount = total_amount,
        order_date = datetime.now()
    )

    new_order.items = order_items

    try:
        db.session.add(new_order)
        db.session.delete(user_cart)
        db.session.commit()
        task.order_successful_mail.delay(new_order.id)
        return {"message": "Order placed successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Failed to place order: {str(e)}"}, 500
        
# FOR TESTING PURPOSE
# IGNORE BELOW CODE

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return {"error": "No image part"}, 400
    file = request.files['image']
    if file.filename == '':
        return {"error": "No selected file"}, 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        new_image = Image(filename=filename)
        db.session.add(new_image)
        db.session.commit()
        return {"message": "Image uploaded successfully"}, 201

@app.route('/images', methods=['GET'])
def get_images():
    images = Image.query.all()
    images_data = []
    for image in images:
        images_data.append({
            'id': image.id,
            'filename': image.filename
        })
    return images_data, 200

@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#TESTING ENDS HERE

@app.route("/getallproductinfo", methods=["GET"])
def getallproductinfo():
    categories = Category.query.all()
    data = []

    for category in categories:
        data.append({
            "id": category.id,
            "name": category.name,
            "products": products_schema.dump(category.products)
        })
    return jsonify(data), 200       
@app.route('/order-history-report', methods=['GET'])
def order_history_report():
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    end_date = datetime(now.year, now.month + 1, 1) - timedelta(days=1) if now.month != 12 else datetime(now.year + 1, 1, 1) - timedelta(days=1)

    # start_date = now - timedelta(days=30)
    # end_date = now

    orders = Order.query.filter(Order.order_date.between(start_date, end_date)).all()

    total_orders = len(orders)
    total_amount = sum(order.total_amount for order in orders)
    total_items = sum(item.quantity for order in orders for item in order.items)

    order_dates = [order.order_date.strftime('%Y-%m-%d') for order in orders]
    order_counts = {date: order_dates.count(date) for date in set(order_dates)}

    plt.figure(figsize=(10, 6))
    plt.bar(order_counts.keys(), order_counts.values())
    plt.xlabel('Date')
    plt.ylabel('Number of Orders')
    plt.title('Number of Orders per Day')
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    response = {
        'total_orders': total_orders,
        'total_amount': total_amount,
        'total_items': total_items,
    }

    return jsonify(response)

@app.route('/order-history-report-graph', methods=['GET'])
def order_history_report_graph():
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route('/order-category-pie-chart', methods=['GET'])
def order_category_pie_chart():
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    end_date = datetime(now.year, now.month + 1, 1) - timedelta(days=1) if now.month != 12 else datetime(now.year + 1, 1, 1) - timedelta(days=1)

    orders = Order.query.filter(Order.order_date.between(start_date, end_date)).all()

    category_counts = {}
    for order in orders:
        for item in order.items:
            category_name = item.product.category.name
            if category_name not in category_counts:
                category_counts[category_name] = 0
            category_counts[category_name] += item.quantity

    plt.figure(figsize=(10, 6))
    plt.pie(category_counts.values(), labels=category_counts.keys(), autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Orders from Different Categories')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)