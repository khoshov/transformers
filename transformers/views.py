from flask import Blueprint, render_template, request
from sqlalchemy import func

from extensions import db
from transformers.models import Transformer, TransformerType

blueprint = Blueprint("transformers", __name__, url_prefix="/")


@blueprint.route("/")
def get_transformer_list():
    name = request.args.get('name', None)
    transformer_type = request.args.get('type', None)

    query = db.select(Transformer)

    if name:
        query = query.filter(func.lower(Transformer.name).contains(name.lower()))

    if transformer_type:
        query = query.filter_by(type=transformer_type)

    transformers = db.session.execute(query).scalars()
    types = db.session.execute(db.select(TransformerType)).scalars()
    return render_template('index.html', transformers=transformers, types=types)


@blueprint.route("/transformers/<int:transformer_id>")
def get_transformer_detail(transformer_id):
    transformer = db.get_or_404(Transformer, transformer_id)
    return render_template("detail.html", transformer=transformer)
