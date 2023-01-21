import os

from flask import url_for
from flask_admin import form
from flask_admin.contrib import sqla
from markupsafe import Markup

import settings

try:
    os.mkdir(settings.MEDIA_DIR)
except OSError:
    pass


class ImageView(sqla.ModelView):
    def __int__(self, static_folder=settings.MEDIA_DIR, *args, **kwargs):
        return super(sqla.ModelView, self).__init__(static_folder=settings.MEDIA_DIR, *args, **kwargs)

    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ''

        return Markup('<img src="%s">' % url_for('core.media', filename=form.thumbgen_filename(model.image)))

    column_formatters = {
        'image': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'image': form.ImageUploadField('Image', base_path=settings.MEDIA_DIR, thumbnail_size=(100, 100, True))
    }
