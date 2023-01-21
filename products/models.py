import settings
from extensions import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    image = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=False)
    transformer = db.Column(db.Integer, db.ForeignKey('transformer.id'), nullable=False)

    @property
    def image_path(self):
        return f'/{settings.MEDIA_DIR}/{self.image}'

    def __repr__(self):
        return self.name
