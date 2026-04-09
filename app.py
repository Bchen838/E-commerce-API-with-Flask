from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy import ForeignKey, Table, Column, String, DateTime, Float, select
from typing import List
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime



# Initialize Flask App
app = Flask(__name__)

# MySQL database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456BrianC$@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating Base Model
class Base(DeclarativeBase):
    pass

# Initizalize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)


# Assoication Table
order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)

# Models
class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))

    user: Mapped["User"] = relationship(back_populates="orders")
    products: Mapped[List["Product"]] = relationship(secondary=order_product, back_populates="orders")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[Float] = mapped_column(Float, nullable=False)
    orders: Mapped[List["Order"]] = relationship(secondary=order_product, back_populates="products")


# Marshmallow Schemas

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product


user_schema = UserSchema()
users_schema = UserSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# GET all users
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.jsonify(users), 200


# GET user by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    return user_schema.jsonify(user), 200

# CREATE new user 
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_user = User(name=user_data['name'], address=user_data['address'],email=user_data['email'])
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201

# Update user by ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    try: 
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user.name = user_data['name']
    user.address = user_data['address']
    user.email = user_data['email']

    db.session.commit()
    return user_schema.jsonify(user), 200


# DELETE user by id
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"successfully deleted user {id}"}), 200



# GET all products
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products), 200

# GET product by id
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    return product_schema.jsonify(product), 200

# CREATE a new product
@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_product = Product(product_name=product_data['product_name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product), 201

# UPDATE product by id
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    product.product_name = product_data['product_name']
    product.price = product_data['price']

    db.session.commit()
    return product_schema.jsonify(product), 200


# DELETE Product by ID
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"sucessfully delete product {id}"}), 200


# CREATE a new order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    user = db.session.get(User, order_data["user_id"])
    if not user:
        return {"error": "User not found"}
    
    new_order = Order(
        user_id=order_data["user_id"],
        order_date=order_data["order_date"]
    )
    
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order), 201

# Add a product to an order
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    
    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    if product in order.products:
        return jsonify({"message": "Product already in order"}), 400
    
    order.products.append(product)
    db.session.commit()
    return jsonify({"message": "Product has been added to order"}), 200

# DELETE a product from an order
@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def delete_productOrder(order_id, product_id):
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)

    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    
    if not product:
        return jsonify({"message": "Invalid product id"}), 400
    
    if product not in order.products:
        return jsonify({"message": "Product in not in the order"}), 400
    
    order.products.remove(product)
    db.session.commit()
    return jsonify({"message": "Product has been removed from order"}), 200

# GET all orders for a user 
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_orders(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400
    
    query = select(Order).where(Order.user_id == user_id)
    orders = db.session.execute(query).scalars().all()

    return orders_schema.jsonify(orders), 200

# Get all products for an order
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_productOrders(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({"message": "Invalid order id"}), 400
    
    products = order.products
    
    return products_schema.jsonify(products), 200
    



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)