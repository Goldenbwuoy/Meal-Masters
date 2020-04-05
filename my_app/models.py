from my_app import db, app, login_manager
from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView


@login_manager.user_loader
def load_customer(customer_id):
    return Customer.query.get(int(customer_id))


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __refr__(self):
        return f"Customer('{self.username}', '{self.email}')"


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(30), nullable=False)
    image_file = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"Meal('{self.name}', '{self.category}')"


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meal = db.Column(db.String(50), nullable=False, unique=False)
    quantity = db.Column(db.String(20), unique=False, nullable=False)
    location = db.Column(db.String(50), unique=False, nullable=False)
    customer = db.Column(db.String(50), unique=False, nullable=False)

    def __repr__(self):
        return f"Orders('{self.quantity}', '{self.location}')"


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), unique=False, nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}')"
