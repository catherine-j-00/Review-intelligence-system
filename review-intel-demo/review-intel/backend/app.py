
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from .config import Config
from .database.db import db
from .routes import (
    auth,
    analyze,
    reviews,
    lookups,
    analytics,
    assistant,
    customer_reviews,
)


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(
        app,
        origins=[app.config["FRONTEND_ORIGIN"]]
    )

    db.init_app(app)
    JWTManager(app)

    for module in (
        auth,
        analyze,
        reviews,
        lookups,
        analytics,
        assistant,
        customer_reviews,
    ):
        app.register_blueprint(module.bp)

    with app.app_context():
        db.create_all()

    return app
