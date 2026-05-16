from datetime import date
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func
from app import db
from app.models.transaction import Transaction
from app.models.product import Product

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    today = date.today()

    today_count = Transaction.query.filter(
        func.date(Transaction.created_at) == today
    ).count()

    today_revenue = (
        db.session.query(func.sum(Transaction.total_amount))
        .filter(func.date(Transaction.created_at) == today)
        .scalar()
        or 0
    )

    total_products = Product.query.filter_by(is_active=True).count()

    low_stock_count = Product.query.filter(
        Product.is_active == True, Product.stock < 10
    ).count()

    recent_transactions = (
        Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
    )

    return render_template(
        'dashboard/index.html',
        today_count=today_count,
        today_revenue=today_revenue,
        total_products=total_products,
        low_stock_count=low_stock_count,
        recent_transactions=recent_transactions,
    )
