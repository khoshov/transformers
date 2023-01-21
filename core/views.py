from flask import Blueprint, send_from_directory

import settings

blueprint = Blueprint("core", __name__, url_prefix="/")


@blueprint.route('/media/<path:filename>')
def media(filename):
    return send_from_directory(settings.MEDIA_DIR, filename)
