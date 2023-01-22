import settings
from extensions import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String, nullable=True)
    url = db.Column(db.String, nullable=False)
    transformer = db.Column(db.Integer, db.ForeignKey('transformer.id'), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    @property
    def image_path(self):
        return f'/{settings.MEDIA_DIR}/{self.image}'

    def __repr__(self):
        return self.name
