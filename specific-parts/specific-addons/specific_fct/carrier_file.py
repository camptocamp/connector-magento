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
        os.chmod(full_path, 0666)
        return result
