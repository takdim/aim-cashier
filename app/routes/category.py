from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.category import Category
from app.utils import admin_required

category_bp = Blueprint('category', __name__, url_prefix='/categories')


@category_bp.route('/')
@login_required
@admin_required
def index():
    categories = Category.query.order_by(Category.name).all()
    return render_template('category/index.html', categories=categories)


@category_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Nama kategori wajib diisi.', 'danger')
        return redirect(url_for('category.index'))

    if Category.query.filter_by(name=name).first():
        flash('Kategori dengan nama tersebut sudah ada.', 'danger')
        return redirect(url_for('category.index'))

    db.session.add(Category(name=name))
    db.session.commit()
    flash(f'Kategori "{name}" berhasil ditambahkan.', 'success')
    return redirect(url_for('category.index'))


@category_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit(id):
    category = Category.query.get_or_404(id)
    name = request.form.get('name', '').strip()
    if not name:
        flash('Nama kategori wajib diisi.', 'danger')
        return redirect(url_for('category.index'))

    existing = Category.query.filter_by(name=name).first()
    if existing and existing.id != id:
        flash('Nama kategori sudah digunakan.', 'danger')
        return redirect(url_for('category.index'))

    category.name = name
    db.session.commit()
    flash('Kategori berhasil diperbarui.', 'success')
    return redirect(url_for('category.index'))


@category_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    category = Category.query.get_or_404(id)
    if category.products:
        flash(
            f'Kategori "{category.name}" tidak dapat dihapus karena masih memiliki produk.',
            'danger',
        )
        return redirect(url_for('category.index'))

    db.session.delete(category)
    db.session.commit()
    flash(f'Kategori "{category.name}" berhasil dihapus.', 'success')
    return redirect(url_for('category.index'))
