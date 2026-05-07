# E-Commerce REST API Overview
This project is a RESTful e-commerce API built using Flask, SQLAlchemy, Marshmallow, and MySQL. The API supports full CRUD operations for users, products, and orders while handling relational database associations through one-to-many and many-to-many relationships.

The application was designed to simulate core backend functionality commonly used in e-commerce platforms, including order management, product relationships, data validation, and database serialization.

## Features
- Full CRUD operations for users, products, and orders
- One-to-many relationship between users and orders
- Many-to-many relationship between orders and products
- Data serialization and validation using Marshmallow schemas
- RESTful API endpoint architecture
- Relational database modeling using SQLAlchemy ORM
- API testing and validation using Postman and MySQL Workbench

## Technologies Used
- Python
- Flask
- SQLAlchemy
- Marshmallow
- MySQL
- Postman
- MySQL Workbench

## API Endpoints
### User Endpoints
- GET /users
- POST /users
- PUT /users/<id>
- DELETE /users/<id>

### Product Endpoints
- GET /products
- POST /products
- PUT /products/<id>
- DELETE /products/<id>

### Order Endpoints
- POST /orders
- PUT /orders/<order_id>/add_product/<product_id>
- DELETE /orders/<order_id>/remove_product/<product_id>
- GET /orders/user/<user_id>

## Installation and Setup
1. Clone the repository and cd
2. Create and activate virtual environment
3. Install dependendecies
4. Configure Database by creating a MySQL database and update the SQLAlchemy database URI configuration inside the application.


### Testing 
Tested using Postman and MySQL Workbench
