import os

from datetime import datetime


def archive_file(filepath):
    path, filename = os.path.split(filepath)
    basename, extension = os.path.splitext(filename)
    now = datetime.now()
    date_str = now.strftime('%Y%m%d%H%M%S')
    new_filename = "%s_%s%s" % (basename, date_str, extension)
    archive_path = os.path.join(path, 'Archive', new_filename)
    return os.renames(filepath, archive_path)
