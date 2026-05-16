from app import db


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    buy_price = db.Column(db.Numeric(12, 2), nullable=False)
    sell_price = db.Column(db.Numeric(12, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    transaction_items = db.relationship('TransactionItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'
