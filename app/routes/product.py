from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.product import Product
from app.models.category import Category
from app.utils import admin_required

product_bp = Blueprint('product', __name__, url_prefix='/products')


@product_bp.route('/')
@login_required
@admin_required
def index():
    q = request.args.get('q', '').strip()
    query = Product.query
    if q:
        query = query.filter(
            Product.name.ilike(f'%{q}%') | Product.sku.ilike(f'%{q}%')
        )
    products = query.order_by(Product.name).all()
    return render_template('product/index.html', products=products, q=q)


@product_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        sku = request.form.get('sku', '').strip()
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id') or None
        buy_price = request.form.get('buy_price', 0)
        sell_price = request.form.get('sell_price', 0)
        stock = request.form.get('stock', 0)

        if not sku or not name:
            flash('SKU dan nama produk wajib diisi.', 'danger')
            return render_template('product/form.html', categories=categories, product=None)

        if Product.query.filter_by(sku=sku).first():
            flash('SKU sudah digunakan produk lain.', 'danger')
            return render_template('product/form.html', categories=categories, product=None)

        try:
            product = Product(
                sku=sku,
                name=name,
                category_id=int(category_id) if category_id else None,
                buy_price=float(buy_price),
                sell_price=float(sell_price),
                stock=int(stock),
                is_active=True,
            )
            db.session.add(product)
            db.session.commit()
            flash(f'Produk "{name}" berhasil ditambahkan.', 'success')
            return redirect(url_for('product.index'))
        except Exception:
            db.session.rollback()
            flash('Terjadi kesalahan saat menyimpan data.', 'danger')

    return render_template('product/form.html', categories=categories, product=None)


@product_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    product = Product.query.get_or_404(id)
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        sku = request.form.get('sku', '').strip()
        name = request.form.get('name', '').strip()
        category_id = request.form.get('category_id') or None
        buy_price = request.form.get('buy_price', 0)
        sell_price = request.form.get('sell_price', 0)
        stock = request.form.get('stock', 0)
        is_active = request.form.get('is_active') == '1'

        if not sku or not name:
            flash('SKU dan nama produk wajib diisi.', 'danger')
            return render_template('product/form.html', categories=categories, product=product)

        existing = Product.query.filter_by(sku=sku).first()
        if existing and existing.id != id:
            flash('SKU sudah digunakan produk lain.', 'danger')
            return render_template('product/form.html', categories=categories, product=product)

        try:
            product.sku = sku
            product.name = name
            product.category_id = int(category_id) if category_id else None
            product.buy_price = float(buy_price)
            product.sell_price = float(sell_price)
            product.stock = int(stock)
            product.is_active = is_active
            db.session.commit()
            flash(f'Produk "{name}" berhasil diperbarui.', 'success')
            return redirect(url_for('product.index'))
        except Exception:
            db.session.rollback()
            flash('Terjadi kesalahan saat menyimpan data.', 'danger')

    return render_template('product/form.html', categories=categories, product=product)


@product_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    product = Product.query.get_or_404(id)
    product.is_active = False  # soft delete
    db.session.commit()
    flash(f'Produk "{product.name}" berhasil dinonaktifkan.', 'success')
    return redirect(url_for('product.index'))
