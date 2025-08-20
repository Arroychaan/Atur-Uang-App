from datetime import date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # "INCOME" atau "EXPENSE". Default ke EXPENSE supaya cocok dengan penggunaan umum kategori.
    kind = db.Column(db.String(20), nullable=False, default="EXPENSE")
    monthly_budget = db.Column(db.Float, nullable=True)  # untuk halaman Budget


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # "INCOME" / "EXPENSE"
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200))
    tx_date = db.Column(db.Date, nullable=False, default=date.today)
