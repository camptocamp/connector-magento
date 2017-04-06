# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Charline Dumontet
#    Copyright 2017 Camptocamp SA
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

from openerp.addons.base_delivery_carrier_files.generator \
    import CarrierFileGenerator
from openerp.tools.translate import _
from openerp.exceptions import Warning
import time


class ColisPriveFileGenerator(CarrierFileGenerator):

    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'colisprive'

    def _generate_files_single(self, pickings, configuration):
        """
        Base method to generate the pickings files, one file per picking
        It returns a list of tuple with a filename, its content and a
        list of pickings ids in the file

        :param browse_record pickings: list of browsable pickings records
        :param browse_record configuration: configuration of
                                            the file to generate
        :return: list of tuple with files to create like:
                 [('filename1', file, [picking ids]),
                  ('filename2', file2, [picking ids])]
        """
        files = []
        today = time.strftime('%Y-%m-%d')
        for picking in pickings:
            if picking.date_done and picking.date_done[:10] < today:
                raise Warning(_("You can't print again a label the day after "
                                "it had been delivered"))

            filename = self._get_filename_single(
                picking, configuration, extension='pdf'
            )
            filename = self.sanitize_filename(filename)
            file_content = self._get_colisprive_file(picking)
            if file_content:
                files.append((filename, file_content, [picking.id]))
        return files

    def _get_colisprive_file(self, picking):
        """
        Create a file in a StringIO, call the method which generates
        the content of the file
        and returns the content of the file

        :param list rows: rows to write in the file, the way they are
                          written to the file is defined in _write_rows
        :param browse_record configuration: configuration of
                                            the file to generate
        :return: content of the file
        """
        file_content = ''
        label = picking._generate_colisprive_label()
        if label and label[0][0].get('file'):
            file_content = label[0][0]['file']
        return file_content