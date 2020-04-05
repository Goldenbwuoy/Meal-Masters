from flask import render_template, flash, redirect, url_for, request
from my_app import app, db, bcrypt
from my_app.models import Meal, Customer, Orders, Admin
from my_app.forms import RegistrationForm, LoginForm, OrderForm, AdminLoginForm
from flask_login import login_user, current_user, logout_user, login_required
import secrets
from PIL import Image
import os


@app.route("/")
def home():
    rice = Meal.query.filter_by(category='rice')
    noodles = Meal.query.filter_by(category='noodles')
    burgers = Meal.query.filter_by(category='burgers')
    dessert = Meal.query.filter_by(category='dessert')
    beverages = Meal.query.filter_by(category='beverages')

    return render_template('home.html', rice=rice, noodles=noodles, burgers=burgers, dessert=dessert, beverages=beverages)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        customer = Customer(username=form.username.data, email=form.email.data,
                            password=hashed_password, mobile_number=form.mobile_number.data)
        db.session.add(customer)
        db.session.commit()
        flash(f'Account created, you can now login', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(
            username=form.username.data).first()
        if customer and bcrypt.check_password_hash(customer.password, form.password.data):
            login_user(customer)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))

        else:
            flash('Login failed, please check your username and password!', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/rice')
def rice():
    rice = Meal.query.filter_by(category='rice')
    return render_template('rice.html', rice=rice)


@app.route('/noodle')
def noodle():
    noodles = Meal.query.filter_by(category='noodles')
    return render_template('noodle.html', noodles=noodles)


@app.route('/burger')
def burger():
    burgers = Meal.query.filter_by(category='burgers')
    return render_template('burger.html', burgers=burgers)


@app.route('/beverage')
def beverage():
    beverages = Meal.query.filter_by(category='beverages')
    return render_template('beverage.html', beverages=beverages)


@app.route('/dessert')
def dessert():
    dessert = Meal.query.filter_by(category='dessert')
    return render_template('dessert.html', dessert=dessert)


@app.route('/view/<int:meal_id>', methods=["GET", "POST"])
def view(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    return render_template('view.html', meal=meal)


@app.route('/view/<int:meal_id>/order', methods=['GET', 'POST'])
@login_required
def order(meal_id):
    meal = Meal.query.get_or_404(meal_id)

    the_meal = meal.name
    quantity = request.form.get("quantity")
    location = request.form.get("location")
    customer = current_user.username

    if quantity and location:
        new_order = Orders(meal=the_meal, quantity=quantity,
                           location=location, customer=customer)
        db.session.add(new_order)
        db.session.commit()
        flash("The order has been successfully placed.", "success")
        return redirect(url_for("home"))

    return render_template('order.html', meal=meal, title='Order')


# Below are all the routes for the Admin side
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(
            username=form.username.data).first()
        if admin and admin.password == form.password.data:
            login_user(admin)

            return redirect(url_for('admin'))

        else:
            flash('Admin login details are invalid, check and try again!', 'danger')
    return render_template('admin/admin_login.html', form=form, title='Admin Login')


@app.route('/admin')
@login_required
def admin():
    return render_template('admin/admin_home.html')


@app.route('/admin/customers', methods=['GET', 'POST'])
def customers():
    customer = Customer.query.all()
    return render_template('admin/customers.html', customer=customer)


@app.route('/admin/meals')
def meals():
    meals = Meal.query.all()
    return render_template('admin/meals.html', meals=meals)


@app.route('/admin/orders')
def orders():
    order = Orders.query.all()
    return render_template('admin/orders.html', order=order)

# A method to save the uploaded picture to the directory
# and return the filename


def save_picure(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/images/meals', picture_fn)
    form_picture.save(picture_path)

    return picture_fn


@app.route('/admin/new_meal', methods=['GET', 'POST'])
def new_meal():
    name = request.form.get("name")
    price = request.form.get("price")
    category = request.form.get("category")
    picture = request.files.get("picture")

    if name and price and category and picture:
        image = save_picure(picture)

        meal = Meal(name=name, price=price,
                    category=category, image_file=image)
        db.session.add(meal)
        db.session.commit()
        flash('The new meal has been added', 'success')
        return redirect(url_for('admin'))

    return render_template('/admin/new_meal.html', title='New meal')


@app.route('/admin/meals/<int:meal_id>/delete')
def delete_meal(meal_id):
    meal = Meal.query.get_or_404(meal_id)
    db.session.delete(meal)
    db.session.commit()
    flash('The meal has been successfully deleted')
    return redirect(url_for('meals'))


@app.route('/admin/orders/<int:order_id>/remove')
@login_required
def remove_order(order_id):
    order = Orders.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Order successfully removed from the list.', 'success')
    return redirect(url_for('orders'))
