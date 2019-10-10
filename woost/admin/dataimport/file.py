"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from shutil import move
from cocktail.jsonutils import json_object

from woost import app
from woost.models.file import File, file_hash
from .dataimport import import_object, Import
from .item import import_item


@import_object.implementation_for(File)
def import_file(self: File, imp: Import, data: json_object):

    upload_id = data.get("_upload")
    import_item(self, imp, data)

    if upload_id:
        upload = app.async_uploader.get(upload_id)
        if not upload:
            raise ValueError("No current upload with id %s" % upload_id)

        # Store file metadata
        self.file_name = upload.name
        self.file_size = upload.size
        self.mime_type = upload.type
        self._v_upload_id = upload_id

        if not imp.dry_run:
            temp_file = app.async_uploader.get_temp_path(upload_id)

            # Compute the file hash
            self.file_hash = file_hash(temp_file)

            # Move the temporary file only after the transaction has been
            # committed
            imp.after_commit(_move_upload, self, temp_file, self.file_path)


def _move_upload(file: File, temp_file: str, dest: str):
    file._v_upload_id = None
    move(temp_file, dest)

