# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import os

from openerp.osv import orm
from openerp.tools.translate import _
from openerp.addons import base_delivery_carrier_files


def write_file(file_path, file_content):
    with open(file_path, 'w') as file_handle:
        file_handle.write(file_content)


# monkey patch _write_file
def _write_file(self, cr, uid, carrier_file, filename, file_content,
                context=None):
    """
    Method responsible of writing the file, on the filesystem or
    by inheriting the module, in the document module as instance

    :param browse_record carrier_file: browsable carrier.file
                                       (configuration)
    :param tuple filename: name of the file to write
    :param tuple file_content: content of the file to write
    :return: True if write is successful
    """
    if not carrier_file.export_path:
        raise orm.except_orm(_('Error'),
                             _('Export path is not defined '
                               'for carrier file %s') %
                             (carrier_file.name,))
    full_path = os.path.join(carrier_file.export_path, filename)
    # ensure file is written only after transaction
    cr.add_transaction_action(write_file, full_path, file_content)
    return True

base_carrier_file = base_delivery_carrier_files.carrier_file.carrier_file
base_carrier_file._write_file = _write_file


class delivery_carrier_file(orm.Model):
    _inherit = 'delivery.carrier.file'

    def _write_file(self, cr, uid, carrier_file, filename, file_content,
                    context=None):
        """
        Method responsible of writing the file, on the filesystem or
        by inheriting the module, in the document module as instance

        :param browse_record carrier_file: browsable carrier.file
                                           (configuration)
        :param tuple filename: name of the file to write
        :param tuple file_content: content of the file to write
        :return: True if write is successful
        """
        result = super(delivery_carrier_file, self)._write_file(
            cr, uid, carrier_file, filename, file_content, context=context)
        full_path = os.path.join(carrier_file.export_path, filename)
        # chronopost needs to drop the file so we have to put the write
        # permission for all users
        cr.add_transaction_action(os.chmod, full_path, 0666)
        return result
