import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskshop import app, db, bcrypt, mail
from flaskshop.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm, ProductForm, CheckoutForm, ContactUsForm)
from flaskshop.models import User, Post, Product, Cart, ContactUs, Order,  MyAdminIndexView, MyModelView
from flask_login import login_user, current_user, logout_user, login_required, LoginManager
from flask_mail import Message
from sqlalchemy import create_engine
from flask import request, jsonify, make_response
#
import sqlite3
from datetime import datetime
import traceback

# Recreate History Table (SQLITE3 module)
# db = sqlite3.connect('flaskshop/site.db')
# c = db.cursor()
# c.execute("DROP TABLE history")
# c.execute("""CREATE TABLE history (time text, email text, action text)""")
# db.commit()


@app.route('/json', methods=['POST'])
def myjson():
    # Validate that there is JSON
    if request.is_json:

        # Parse the JSON into a python dict
        req = request.get_json()

        # if req.get('command'):
        db = sqlite3.connect('flaskshop/site.db')
        c = db.cursor()
        with db:
            c.executescript("INSERT INTO history VALUES ('{}', '{}', '{}')".format(datetime.now().strftime('%d/%m/%y, %H:%M:%S'), req.get('name'), req.get('message')))
        # executescript has no output apparently
        # vv SQLAlchemy way
        # conn = create_engine('sqlite:///flaskshop/site.db')
        # c = conn.connect()
        # lst = c.execute("SELECT * FROM user WHERE email = '{}'".format(req.get('command')))
        # print(lst.fetchone())

        # Return a string along a HTTP code
        # return 'This json lul', 200

        response_body = {
            'message': 'Received!',
            'sender': req.get('name')
        }

        # Create a JSON response
        res = make_response(jsonify(response_body), 200)
        return res
    else:
        response_body = {
            'message': 'No JSON detected!'
        }
        return make_response(jsonify(response_body), 400)


@app.route("/forum")
def forum():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('forum.html', title='Forum', posts=posts)


@app.route("/contact/<int:user_id>", methods=['GET', 'POST'])
def contact(user_id):
    user = User.query.get_or_404(user_id)
    form = ContactUsForm()
    if form.validate_on_submit():
        contact = ContactUs(subject=form.subject.data, content=form.content.data, author=user)
        db.session.add(contact)
        db.session.commit()
        flash(' Your feedback has been sent!', 'success')
        return redirect(url_for('shop'))
    return render_template('contactus.html', title='Contact Us', form =form, legend='New Feedback', user=user)


@app.route("/")
def home():
    # Thomas - unable to integrate vulnerable cookie
    ck = request.cookies.get('userdata')
    print('[HOME] CK ("userdata") ->', ck)
    # # #ALWAYS NEEDED
    conn = sqlite3.connect('my.db')
    c = conn.cursor()
    # # # END
    # c.execute("SELECT * FROM user")
    userdb = c.fetchall()
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=5)
    return render_template('shop.html', userdb=userdb, products=products)


# @app.route('/setck')
# def setck():
#     print('[LOGIN] Generating Cookie')
#     test = make_response(redirect(url_for('home')))
#     print(test)
#     test.set_cookie('userID', current_user.get_id())
#     print('[LOGIN] Cookie generated')
#     print(request.cookies)
#     return test


@app.route("/shop")
def shop():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=5)
    return render_template('shop.html', title="Shop", products=products)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # KEITH: START
        conn = create_engine('sqlite:///flaskshop/site.db')
        c = conn.connect()
        length = c.execute('SELECT * FROM user')
        length = len(length.fetchall()) + 1
        # length = c.execute('SELECT COUNT(*) FROM user') + 1
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        conn.execute("INSERT INTO user VALUES ({}, '{}', '{}', '{}', '{}', {})".format(length, form.username.data, form.email.data,
                                                                         'default.jpg', hashed_password, 0))
        # db.session.commit()
        # KEITH: END
        # JQ: DISABLED
        # hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # db.session.add(user)
        # db.session.commit()
        # JQ: END
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop'))
    form = LoginForm()
    if form.validate_on_submit():
        # KEITH: START
        conn = create_engine('sqlite:///flaskshop/site.db')
        c = conn.connect()
        userdb = c.execute('SELECT email, password FROM user')
        userdb = userdb.fetchall()
        user = None
        tentative = [None, None]
        for val in userdb:
            if val[0] in form.email.data:
                tentative = val
                break
        try:
            print('SELECT * FROM user WHERE email = "{}" AND {}'.format(form.email.data, int(
                                                                                             bcrypt.check_password_hash(
                                                                                                 tentative[1],
                                                                                                 form.password.data))))
            user = c.execute('SELECT * FROM user WHERE email = "{}" AND {}'.format(form.email.data, int(
                                                                                             bcrypt.check_password_hash(
                                                                                                 tentative[1],
                                                                                                 form.password.data))))
            user = user.fetchall()
        except TypeError:
            print('Invalid Login detected.')
        if user:
            # IF SUCCESSFUL THEN
            user = User.query.filter_by(email=val[0]).first()
            login_user(user, remember=form.remember.data)
            # ck = make_response(redirect(url_for('home')))
            # print(current_user.get_id() + ' ' + str(current_user.is_admin()))
            # ck.set_cookie('userdata', value=current_user.get_id() + ' ' + str(current_user.is_admin()))
            # print('[LOGIN] Cookie generated')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('shop'))#ck(returning ck results in TypeError)
        else:
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('Login Unsuccessful. Email is valid but password is incorrect', 'danger')
            else:
                flash('Login Unsuccessful. Email is invalid as it has not been registered yet', 'danger')
        # KEITH: END

        # JQ: DISABLED
        # user = User.query.filter_by(email=form.email.data).first()
        # print(user)
        # if user and bcrypt.check_password_hash(user.password, form.password.data):
        #     login_user(user, remember=form.remember.data)
        #     next_page = request.args.get('next')
        #     return redirect(next_page) if next_page else redirect(url_for('shop'))
        # else:
        #     flash('Login Unsuccessful. Please check email and password', 'danger')
        # JQ: END
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('shop'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account/<int:user_id>", methods=['GET', 'POST'])
@login_required
def account(user_id):
    user = User.query.get_or_404(user_id)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            user.image_file = picture_file
        user.username = form.username.data
        user.email = form.email.data
        # Thomas: included password data in profile
        user.password = form.password.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account', user_id=user.id))
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.password.data = user.password
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form, user=user)


@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('forum'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    #if post.author != current_user:
        #abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    #if post.author != current_user:
        #abort(403)
    db.session.delete(post)
    db.session.commit()

    flash('Your post has been deleted!', 'success')
    return redirect(url_for('forum'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('shop'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('shop'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data, price=form.price.data, qty=form.qty.data)
        db.session.add(product)
        db.session.commit()
        flash('Product has been added!', 'success')
        return redirect(url_for('shop'))
    return render_template('create_product.html', title='New Product',
                           form=form, legend='New Product')


@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', name=product.name, product=product)


@app.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if current_user.admin_rights is False:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        product.price = form.price.data
        product.qty = form.qty.data
        db.session.commit()
        flash('Product has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.name.data = product.name
        form.price.data = product.price
        form.qty.data = product.qty
    return render_template('create_product.html', title='Update Product',
                           form=form, legend='Update Product')


@app.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if current_user.admin_rights is False:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Your product has been deleted!', 'success')
    return redirect(url_for('shop'))


@app.route("/cart", methods=['GET'])
@login_required
def cart():
    page = request.args.get('page', 1, type=int)
    product = Product.query.order_by(Product.id.desc()).paginate(page=page, per_page=5)
    cart_items = Cart.query.order_by(Cart.id.desc()).paginate(page=page, per_page=5)
    return render_template('cart.html', title="Cart", cart_items=cart_items, product=product)


@app.route("/add_to_cart/<int:product_id>", methods=["GET", "POST"])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = Cart(product_id=product_id, product_name=product.name, qty=1, price=product.price, owner_id=current_user.id)
    exisitng_item = Cart.query.filter_by(owner_id=current_user.id, product_id=product.id).first()
    if exisitng_item is None:
        db.session.add(cart)
        db.session.commit()
    else:
        exisitng_item.qty = exisitng_item.qty + 1
        db.session.commit()
    flash('Product has been added to you shopping cart', 'success')
    return redirect(url_for('cart'))


@app.route("/remove_from_cart/<int:product_id>")
@login_required
def remove_from_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = Cart.query.filter_by(owner_id=current_user.id, product_id=product.id).first_or_404()
    db.session.delete(cart)
    db.session.commit()
    return redirect(url_for('cart'))


@app.route("/checkout", methods=['GET','POST'])
@login_required
def checkout():
    qty = []
    price = []
    prod_name = []
    form = CheckoutForm()
    cart = Cart.query.filter_by(owner_id=current_user.id).all()
    print(cart)
    for i in cart:
        qty.append(i.qty)
        price.append('%.2f' % i.price)
        prod_name.append(i.product_name)
    prod_name = ','.join(prod_name)
    strprice = ','.join("'{0}'".format(n) for n in price)
    strqty = ','.join("'{0}'".format(n) for n in qty)
    print(strqty)
    print(strprice)
    print(prod_name)
    temptotalsum = [int(float(price)) * qty for price, qty in zip(price, qty)]
    print(temptotalsum)
    if form.validate_on_submit():
        order = Order(address=form.address.data, postal=form.postal.data, cardNumber=form.cardNumber.data,
                      expDate=form.expDate.data, cvv=form.cvv.data, product_name=prod_name,
                      price=strprice, qty=strqty, totalsum=sum(temptotalsum), owner_id=current_user.id)
        for i in cart:
            db.session.delete(i)
        db.session.add(order)
        db.session.commit()
        flash('Your order has been submitted!', 'success')
        return redirect(url_for('orders'))
    return render_template('checkout.html', title='Checkout',
                           form=form, legend='Checkout', cart=cart)


@app.route("/orders", methods=['GET', 'POST'])
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    order = Order.query.order_by(Order.id.desc()).paginate(page=page, per_page=5)
    return render_template('orders.html', title="Orders", order=order)


@app.errorhandler(404)
def page_not_found(exception):
    return traceback.format_exc()
