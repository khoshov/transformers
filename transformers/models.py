import settings
from extensions import db

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
        return f'/{settings.MEDIA_DIR}/{self.image}'

    def __repr__(self):
        return self.name
