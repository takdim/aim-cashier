from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Silakan login terlebih dahulu.'
login_manager.login_message_category = 'warning'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    @app.context_processor
    def inject_user():
        return {'current_user': current_user}

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.product import product_bp
    from app.routes.category import category_bp
    from app.routes.user_mgmt import user_bp
    from app.routes.transaction import transaction_bp
    from app.routes.report import report_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(report_bp)

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    return app
