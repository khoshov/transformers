from flask import Flask
from flask_admin.contrib import sqla

from admin import ImageView
from extensions import admin, db, migrate
from products.models import Product
from transformers.models import Transformation, Transformer, TransformerType
from . import contacts, core, transformers, commands


def create_app(config_object="settings"):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_admin()
    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app)


def register_blueprints(app):
    app.register_blueprint(contacts.views.blueprint)
    app.register_blueprint(core.views.blueprint)
    app.register_blueprint(transformers.views.blueprint)


def register_commands(app):
    app.cli.add_command(commands.collect_data)


def register_admin():
    admin.add_view(ImageView(Transformer, db.session))
    admin.add_view(ImageView(Product, db.session))
    admin.add_view(sqla.ModelView(Transformation, db.session))
    admin.add_view(sqla.ModelView(TransformerType, db.session))
