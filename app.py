from flask import Flask, render_template, send_from_directory, url_for
from flask_admin.contrib import sqla
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os.path
from flask_admin import Admin, form

from markupsafe import Markup

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)
migrate = Migrate(app, db)
admin = Admin(app, 'Transformers', template_mode='bootstrap4')

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['SECRET_KEY'] = '123456790'
app.config['MEDIA_PATH'] = 'media'


file_path = os.path.join(os.path.dirname(__file__), app.config['MEDIA_PATH'])

try:
    os.mkdir(file_path)
except OSError:
    pass


transformations = db.Table(
    'transformations',
    db.Column('transformer_id', db.Integer, db.ForeignKey('transformer.id'), primary_key=True),
    db.Column('transformation_id', db.Integer, db.ForeignKey('transformation.id'), primary_key=True)
)


class Transformation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return self.name


class TransformerType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    transformers = db.relationship('Transformer', backref='types', lazy=True)

    def __repr__(self):
        return self.name


class Transformer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.String, nullable=False)
    type = db.Column(db.Integer, db.ForeignKey('transformer_type.id'), nullable=False)
    motto = db.Column(db.Text)
    transformations = db.relationship(
        'Transformation',
        secondary=transformations,
        lazy='subquery',
        backref=db.backref('transformers', lazy=True)
    )
    products = db.relationship('Product', backref='transformers', lazy=True)

    @property
    def image_path(self):
        return f'/{app.config["MEDIA_PATH"]}/{self.image}'

    def __repr__(self):
        return self.name


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    transformer = db.Column(db.Integer, db.ForeignKey('transformer.id'), nullable=False)

    @property
    def image_path(self):
        return f'/{app.config["MEDIA_PATH"]}/{self.image}'

    def __repr__(self):
        return self.name


class ImageView(sqla.ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ''

        return Markup('<img src="%s">' % url_for('media', filename=form.thumbgen_filename(model.image)))

    column_formatters = {
        'image': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'image': form.ImageUploadField('Image', base_path=file_path, thumbnail_size=(100, 100, True))
    }


@app.route('/')
def get_transformer_list():  # put application's code here
    transformers = db.session.execute(db.select(Transformer)).scalars()
    return render_template('index.html', transformers=transformers)


@app.route("/transformers/<int:transformer_id>")
def get_transformer_detail(transformer_id):
    transformer = db.get_or_404(Transformer, transformer_id)
    return render_template("detail.html", transformer=transformer)


@app.route("/contacts")
def get_contacts():
    return render_template("contacts.html")


@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(app.config['MEDIA_PATH'], filename)


admin.add_view(ImageView(Transformer, db.session))
admin.add_view(ImageView(Product, db.session))
admin.add_view(sqla.ModelView(Transformation, db.session))
admin.add_view(sqla.ModelView(TransformerType, db.session))


@app.cli.command("collect-data")
def collect_transformers_data():
    pass


if __name__ == '__main__':
    app.run()
