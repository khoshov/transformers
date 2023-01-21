from flask import Blueprint, render_template

blueprint = Blueprint("contacts", __name__, url_prefix="/contacts")


@blueprint.route("/")
def get_contacts():
    return render_template("contacts.html")
