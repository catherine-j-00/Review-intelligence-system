from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .db import db


class Brand(db.Model):
    __tablename__ = 'brands'
    brand_id = db.Column(db.Integer, primary_key=True)
    brand_name = db.Column(db.String(120), unique=True, nullable=False)


class Category(db.Model):
    __tablename__ = 'categories'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(120), unique=True, nullable=False)


class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(200), nullable=False)
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.brand_id'), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    brand = db.relationship('Brand', backref='products')
    category = db.relationship('Category', backref='products')
    __table_args__ = (db.UniqueConstraint('product_name', 'brand_id', name='uq_product_brand'),)


class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(100), unique=True)  # id from your CSV or shop API
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), index=True)
    review_text = db.Column(db.Text, nullable=False)
    review_date = db.Column(db.Date, index=True)
    is_sample = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='reviews')
    analysis = db.relationship('ReviewAnalysis', uselist=False, backref='review',
                               cascade='all, delete-orphan')


class ReviewAnalysis(db.Model):
    __tablename__ = 'review_analysis'
    analysis_id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.review_id'), unique=True, nullable=False)
    sentiment = db.Column(db.String(20), index=True, nullable=False)
    emotion = db.Column(db.String(50), index=True, nullable=False)
    confidence_score = db.Column(db.Float)
    needs_review = db.Column(db.Boolean, default=False)  # low-confidence flag
    model_version = db.Column(db.String(50))
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)
