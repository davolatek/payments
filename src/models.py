import random
import string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(), nullable=False)
    account = db.relationship("Accounts", backref="user")
    created_at = db.Column(db.DateTime(), default=datetime.now())
    updated_at = db.Column(db.DateTime(), onupdate=datetime.now())

    def __repr__(self) -> str:
        return 'User>>> {self.email}'


class Accounts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(10), nullable=False)
    account_balance = db.Column(db.Double(), default=0.00)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now())

    def generate_account_number(self):
        account_number = ''.join(random.choices(string.digits, k=10))
        return account_number

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.account_number = self.generate_account_number()


    def __repr__(self) -> str:
        return 'Accounts>>> {self.id}'
    

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_amount = db.Column(db.Double(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    transaction_type = db.Column(db.String(), nullable=False)
    transaction_description = db.Column(db.String(), nullable=False)
    transaction_location = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.now())


    def __repr__(self) -> str:
        return 'Accounts>>> {self.id}'
