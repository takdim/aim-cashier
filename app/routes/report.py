import csv
import io
from datetime import date, datetime
from flask import Blueprint, render_template, request, Response
from flask_login import login_required
from sqlalchemy import func
from app import db
from app.models.transaction import Transaction
from app.models.product import Product
from app.utils import admin_required

report_bp = Blueprint('report', __name__, url_prefix='/reports')


def _parse_date(value, fallback):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return fallback


@report_bp.route('/sales')
@login_required
@admin_required
def sales():
    today = date.today()
    start_date = _parse_date(request.args.get('start'), today)
    end_date = _parse_date(request.args.get('end'), today)

    transactions = Transaction.query.filter(
        func.date(Transaction.created_at) >= start_date,
        func.date(Transaction.created_at) <= end_date,
    ).order_by(Transaction.created_at.desc()).all()

    total_revenue = sum(float(t.total_amount) for t in transactions)

    return render_template(
        'report/sales.html',
        transactions=transactions,
        total_revenue=total_revenue,
        start_date=start_date,
        end_date=end_date,
    )


@report_bp.route('/sales/export/csv')
@login_required
@admin_required
def export_sales_csv():
    today = date.today()
    start_date = _parse_date(request.args.get('start'), today)
    end_date = _parse_date(request.args.get('end'), today)

    transactions = Transaction.query.filter(
        func.date(Transaction.created_at) >= start_date,
        func.date(Transaction.created_at) <= end_date,
    ).order_by(Transaction.created_at.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['No. Struk', 'Kasir', 'Total', 'Bayar', 'Kembalian', 'Waktu'])
    for t in transactions:
        writer.writerow([
            t.invoice_no,
            t.user.name,
            float(t.total_amount),
            float(t.paid_amount),
            float(t.change_amount),
            t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    output.seek(0)
    filename = f"laporan_penjualan_{start_date}_{end_date}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


@report_bp.route('/stock')
@login_required
@admin_required
def stock():
    products = Product.query.filter_by(is_active=True).order_by(Product.stock.asc()).all()
    return render_template('report/stock.html', products=products, threshold=10)
