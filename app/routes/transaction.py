from datetime import date
from flask import Blueprint, render_template, request, jsonify, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from app import db
from app.models.transaction import Transaction, TransactionItem
from app.models.product import Product

transaction_bp = Blueprint('transaction', __name__)


def _generate_invoice_no():
    today = date.today()
    prefix = f"INV-{today.strftime('%Y%m%d')}-"
    count = Transaction.query.filter(
        func.date(Transaction.created_at) == today
    ).count()
    return f"{prefix}{str(count + 1).zfill(3)}"


@transaction_bp.route('/pos')
@login_required
def pos():
    return render_template('transaction/pos.html')


@transaction_bp.route('/pos/search')
@login_required
def pos_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    products = Product.query.filter(
        Product.is_active == True,
        Product.stock > 0,
        Product.name.ilike(f'%{q}%') | Product.sku.ilike(f'%{q}%'),
    ).limit(10).all()

    return jsonify([
        {
            'id': p.id,
            'sku': p.sku,
            'name': p.name,
            'sell_price': float(p.sell_price),
            'stock': p.stock,
        }
        for p in products
    ])


@transaction_bp.route('/pos/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Data tidak valid.'}), 400

    items = data.get('items', [])
    if not items:
        return jsonify({'success': False, 'message': 'Keranjang kosong.'}), 400

    try:
        paid_amount = float(data.get('paid_amount', 0))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Nominal pembayaran tidak valid.'}), 400

    total_amount = 0
    validated_items = []

    for item in items:
        try:
            product_id = int(item['product_id'])
            quantity = int(item['quantity'])
            unit_price = float(item['unit_price'])
        except (KeyError, ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Data item tidak valid.'}), 400

        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Jumlah item harus lebih dari 0.'}), 400

        product = Product.query.get(product_id)
        if not product or not product.is_active:
            return jsonify({'success': False, 'message': 'Produk tidak ditemukan.'}), 400

        if product.stock < quantity:
            return jsonify({
                'success': False,
                'message': f'Stok "{product.name}" tidak cukup. Tersedia: {product.stock}',
            }), 400

        subtotal = unit_price * quantity
        total_amount += subtotal
        validated_items.append({
            'product': product,
            'quantity': quantity,
            'unit_price': unit_price,
            'subtotal': subtotal,
        })

    if paid_amount < total_amount:
        return jsonify({
            'success': False,
            'message': f'Uang yang dibayar kurang dari total Rp {total_amount:,.0f}',
        }), 400

    change_amount = paid_amount - total_amount

    try:
        invoice_no = _generate_invoice_no()
        transaction = Transaction(
            invoice_no=invoice_no,
            user_id=current_user.id,
            total_amount=total_amount,
            paid_amount=paid_amount,
            change_amount=change_amount,
        )
        db.session.add(transaction)
        db.session.flush()

        for item in validated_items:
            db.session.add(TransactionItem(
                transaction_id=transaction.id,
                product_id=item['product'].id,
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                subtotal=item['subtotal'],
            ))
            item['product'].stock -= item['quantity']

        db.session.commit()
        return jsonify({'success': True, 'transaction_id': transaction.id, 'invoice_no': invoice_no})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Terjadi kesalahan server.'}), 500


@transaction_bp.route('/transactions')
@login_required
def history():
    if current_user.role == 'admin':
        transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    else:
        transactions = Transaction.query.filter_by(
            user_id=current_user.id
        ).order_by(Transaction.created_at.desc()).all()
    return render_template('transaction/history.html', transactions=transactions)


@transaction_bp.route('/transactions/<int:id>')
@login_required
def detail(id):
    transaction = Transaction.query.get_or_404(id)
    if current_user.role != 'admin' and transaction.user_id != current_user.id:
        abort(403)
    return render_template('transaction/detail.html', transaction=transaction)
