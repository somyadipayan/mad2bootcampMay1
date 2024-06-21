from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
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


class Category(db.Model):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    creator_email = Column(Text, db.ForeignKey('user.email') ,nullable=False)
    creator = relationship('User', backref='categories')
    products = relationship('Product', back_populates='category', cascade= "all, delete-orphan")
    verified = Column(Boolean, nullable=False)

    def __init__(self, name, creator_email, verified):
        self.name = name
        self.creator_email = creator_email
        self.verified = verified


class Product(db.Model):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    unit = Column(Text, nullable=False) # KG, Piece, Litres
    rateperunit = Column(Integer, nullable=False) 
    quantity = Column(Integer, nullable=False)
    category_id = Column(Integer, db.ForeignKey('category.id'), nullable=False)
    category = relationship('Category', back_populates='products')
    creator_email = Column(Text, db.ForeignKey('user.email') ,nullable=False)
    creator = relationship('User', backref='products')
    shoppingcarts = relationship('CartItems', back_populates='product', cascade= "all, delete-orphan")
    orders = relationship('OrderItems', back_populates='product', cascade= "all, delete-orphan")

    def __init__(self, name, unit, rateperunit, quantity, category_id, creator_email):
        self.name = name
        self.unit = unit
        self.rateperunit = rateperunit
        self.quantity = quantity
        self.category_id = category_id
        self.creator_email = creator_email

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'creator_email', 'verified')

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'unit', 'rateperunit', 'quantity', 'category_id', 'creator_email')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

class ShoppingCart(db.Model):
    __tablename__ = 'shoppingcart'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(Text, db.ForeignKey('user.email') ,nullable=False)
    user = relationship('User', backref='shoppingcart')
    items = relationship('CartItems', back_populates='shoppingcart', cascade= "all, delete-orphan")

class CartItems(db.Model):
    __tablename__ = 'cartitem'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, db.ForeignKey('product.id'), nullable=False)
    shoppingcart_id = Column(Integer, db.ForeignKey('shoppingcart.id'), nullable=False)
    shoppingcart = relationship('ShoppingCart', back_populates='items')
    product = relationship('Product', back_populates='shoppingcarts')
    quantity = Column(Integer, nullable=False)

class Order(db.Model):
    __tablename__ = 'order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(Text, db.ForeignKey('user.email') ,nullable=False)
    user = relationship('User', backref='orders')
    items = relationship('OrderItems', back_populates='order', cascade= "all, delete-orphan")
    total_amount = Column(Integer, nullable=False)
    order_date = Column(DateTime, nullable=False)

class OrderItems(db.Model):
    __tablename__ = 'orderitem'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, db.ForeignKey('product.id'), nullable=False)
    order_id = Column(Integer, db.ForeignKey('order.id'), nullable=False)
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='orders')
    quantity = Column(Integer, nullable=False)