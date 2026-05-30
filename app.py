from flask import Flask

from cli import register_cli
from config import Config
from extensions import close_db
from models import init_db
from routes import main_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    app.teardown_appcontext(close_db)
    app.register_blueprint(main_bp)
    register_cli(app)

    with app.app_context():
        init_db()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
