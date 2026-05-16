from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db, bcrypt
from app.models.user import User
from app.utils import admin_required

user_bp = Blueprint('user', __name__, url_prefix='/users')


@user_bp.route('/')
@login_required
@admin_required
def index():
    users = User.query.order_by(User.name).all()
    return render_template('user/index.html', users=users)


@user_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'kasir')

        if not name or not username or not password:
            flash('Semua field wajib diisi.', 'danger')
            return render_template('user/form.html', user=None)

        if len(password) < 6:
            flash('Password minimal 6 karakter.', 'danger')
            return render_template('user/form.html', user=None)

        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan.', 'danger')
            return render_template('user/form.html', user=None)

        user = User(
            name=name,
            username=username,
            password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
            role=role,
            is_active=True,
        )
        db.session.add(user)
        db.session.commit()
        flash(f'Pengguna "{name}" berhasil ditambahkan.', 'success')
        return redirect(url_for('user.index'))

    return render_template('user/form.html', user=None)


@user_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'kasir')
        is_active = request.form.get('is_active') == '1'

        if not name or not username:
            flash('Nama dan username wajib diisi.', 'danger')
            return render_template('user/form.html', user=user)

        existing = User.query.filter_by(username=username).first()
        if existing and existing.id != id:
            flash('Username sudah digunakan pengguna lain.', 'danger')
            return render_template('user/form.html', user=user)

        if password:
            if len(password) < 6:
                flash('Password minimal 6 karakter.', 'danger')
                return render_template('user/form.html', user=user)
            user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        user.name = name
        user.username = username
        user.role = role
        user.is_active = is_active
        db.session.commit()
        flash(f'Pengguna "{name}" berhasil diperbarui.', 'success')
        return redirect(url_for('user.index'))

    return render_template('user/form.html', user=user)


@user_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
@admin_required
def toggle(id):
    user = User.query.get_or_404(id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'diaktifkan' if user.is_active else 'dinonaktifkan'
    flash(f'Pengguna "{user.name}" berhasil {status}.', 'success')
    return redirect(url_for('user.index'))
