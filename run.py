import os
from app import create_app, db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.transaction import Transaction, TransactionItem
from flask_bcrypt import Bcrypt

app = create_app(os.environ.get('FLASK_ENV', 'default'))
_bcrypt = Bcrypt(app)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        User=User,
        Category=Category,
        Product=Product,
        Transaction=Transaction,
        TransactionItem=TransactionItem,
    )


@app.cli.command('init-db')
def init_db():
    """Membuat tabel database dan akun admin awal."""
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(
            name='Administrator',
            username='admin',
            password_hash=_bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin',
            is_active=True,
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin berhasil dibuat  →  username: admin  |  password: admin123')
    else:
        print('Akun admin sudah ada.')


if __name__ == '__main__':
    app.run()
