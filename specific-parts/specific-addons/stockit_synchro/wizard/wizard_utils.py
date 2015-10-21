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
    os.renames(filepath, archive_path)
    return archive_path


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


def create_claim(self, cr, uid, title, message, filename, file_data,
                 categ_id, context=None):
    """ Create new claim for the error """
    try:
        __, section_id = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'stockit_synchro', 'section_stockit_error')
        claim_vals = {'name': title,
                      'description': message,
                      'categ_id': categ_id,
                      'section_id': section_id,
                      'claim_type': 'other'}
        claim_id = self.pool['crm.claim'].create(cr, uid, claim_vals,
                                                 context=context)
        # Add file as attachment
        attachment_data = {
            'name': filename,
            'datas': file_data,
            'datas_fname': filename,
            'res_model': 'crm.claim',
            'res_id': claim_id,
        }
        self.pool['ir.attachment'].create(cr, uid, attachment_data,
                                          context=context)
    except ValueError:
        _logger.error('Could not create a claim about the error')
