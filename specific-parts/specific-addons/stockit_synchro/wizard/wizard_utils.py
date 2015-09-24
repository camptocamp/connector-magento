# -*- coding: utf-8 -*-
import logging
import os

from datetime import datetime


_logger = logging.getLogger(__name__)


def archive_file(filepath, in_error=False):
    path, filename = os.path.split(filepath)
    basename, extension = os.path.splitext(filename)
    now = datetime.now()
    date_str = now.strftime('%Y%m%d%H%M%S')
    new_filename = "%s_%s%s" % (basename, date_str, extension)
    # If file is in error we archive it in ERROR directory
    if in_error:
        archive_path = os.path.join(path, 'ERREUR', new_filename)
    else:
        archive_path = os.path.join(path, 'Archive', new_filename)
    return os.renames(filepath, archive_path)


def post_message(self, cr, uid, message,
                 subtype='mail.mt_comment',
                 context=None):
    """ Post an error message on the mail group """
    data_obj = self.pool['ir.model.data']
    mail_group_obj = self.pool['mail.group']
    try:
        __, mail_group_id = data_obj.get_object_reference(
            cr, uid, 'stockit_synchro', 'group_import_export_stockit')
        mail_group_obj.message_post(
            cr, uid, [mail_group_id],
            body=message,
            subtype=subtype,
            context=context)
    except ValueError:
        _logger.error('Could not post a notification about the error '
                      'because the Stockit mail group has been deleted')
