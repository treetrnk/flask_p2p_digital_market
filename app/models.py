import pytz
import requests
from flask import current_app, url_for, session, jsonify, render_template
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime, timedelta, timezone
from time import sleep
from markdown import markdown
from sqlalchemy import desc
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import backref
from flask_mail import Mail, Message
from app import mail
from app.email import send_email

products = db.Table('products',
    db.Column('product_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True)
)

########
# USER #
########
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(64), index=True, unique=True)
    avatar = db.Column(db.String(500))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    timezone = db.Column(db.String(150))
    last_login = db.Column(db.DateTime)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)
    
    def display_name(self):
        if self.name:
            return self.name
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<User({self.username})>"
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

#########
# ALIAS #
#########
class Alias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=backref('aliases', order_by='Alias.name'), lazy=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Name({self.name})>"
    
###########
# LISTING #
###########
class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category1 = db.Column(db.String(150), nullable=False)
    category2 = db.Column(db.String(150))
    category3 = db.Column(db.String(150))
    category4 = db.Column(db.String(150))
    alias_id = db.Column(db.Integer, db.ForeignKey('alias.id'))
    user = db.relationship('Alias', backref=backref('listings', order_by='Listing.category1,Listing.name'), lazy=True)
    alias_id = 
    alias = 
    contributors = db.Column(db.String(1000))

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Listing({self.name})>"
    
###########
# PRODUCT #
###########
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    barcode = db.Column(db.String(150))
    sku = db.Column(db.String(150))
    seller_sku = db.Column(db.String(150))
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'))
    listing = db.relationship('Listing', backref=backref('products', order_by='Product.name,Product.barcode'), lazy=True)
    file = 

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Product({self.name})>"
    
#########
# ORDER #
#########
class Order(db.model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=backref('orders', order_by='Alias.name'), lazy=True)
    products = db.relationship('Product', secondary=products, lazy='subquery', 
            backref=db.backref('orders', order_by='Order.created', lazy=True))
    status_url = db.Column(db.String(1000))
    coupons = db.Column(db.String(250)) 
    discounts = db.Column(db.Decimal(24,24))
    donation = db.Column(db.Decimal(24,24))
    total = db.Column(db.Decimal(24,24))
    donation = db.Column(db.Decimal(24,24))
    status = db.Column(db.String(150))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)

    def total_to_send(self):
        donation = self.donation or 0
        discounts = self.discounts or 0
        return self.total - self.donation - self.discounts

    def __str__(self):
        return self.session_id

    def __repr__(self):
        return f"<Order({self.session_id}, {self.total}, {self.created})>"

STATUS_CHOICES = [
        ('incomplete', 'Incomplete'), # Items in cart
        ('awaiting-payment', 'Awaiting Payment'), # Buyer submitted purchase request
        ('confirmed', 'Confirmed'), # Payment received by website admin and files sent to buyer
        ('complete', 'Complete') # When payment has been sent to seller
    ]
