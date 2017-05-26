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
from openerp.addons.base_delivery_carrier_files.generator import BaseLine
from openerp.addons.base_delivery_carrier_files.csv_writer \
    import UnicodeWriter
from datetime import datetime
from openerp.osv import orm
from tools.translate import _
from unidecode import unidecode

REQUIRED_FIELDS = {
    'record_type':  _('Record type'),
    'product_code': _('Product code'),
    'recipient_name': _('Recipient name'),
    'address_3': _('Recipient first address'),
    'recipient_zip': _('Recipient zip'),
    'recipient_town': _('Recipient city'),
    'exped_trading_name': _('Expeditor trading name'),
}

MR = ['Monsieur', 'M.', 'M', 'Mr.', 'Mr']
MME = ['Madame', 'Mme', 'Mme.']
MLLE = ['Mademoiselle', 'Mlle', 'Mlle.']


class ColissimoLine(BaseLine):
    fields = (('record_type', [3, 1]),
              ('parcel_reference', [35, 4]),
              ('exped_date', [8, 39]),
              ('product_code', [4, 47]),
              ('recipient_name', [35, 74]),
              ('address_3', [35, 109]),
              ('address_2', [35, 144]),
              ('address_1', [35, 179]),
              ('recipient_zip', [9, 214]),
              ('recipient_town', [35, 223]),
              ('recipient_country_code', [3, 258]),
              ('delivery_instructions', [70, 261]),
              ('weight', [15, 343]),
              ('phone_nb', [25, 412]),
              ('recipient_mail', [75, 445]),
              ('address_4', [35, 600]),
              ('order_nb', [35, 670]),
              ('recipient_title', [1, 778]),
              ('recipient_first_name', [29, 779]),
              ('recipient_busi_name', [38, 808]),
              ('recipient_mobile', [10, 846]),
              ('parcel_point', [6, 902]),
              ('exped_trading_name', [38, 909]),)


class ColissimoRows(object):

    def __init__(self, picking, configuration, package_nb):
        self.picking = picking
        self.configuration = configuration
        self.package_nb = package_nb

    def _line(self):
        picking = self.picking
        package_nb = self.package_nb
        carrier = picking.carrier_id
        datetime_date_done = datetime.strptime(picking.date_done,
                                               '%Y-%m-%d %H:%M:%S')
        date_done = datetime.strftime(datetime_date_done, '%Y-%m-%d %H:%M:%S')

        line = ColissimoLine()
        # Configuration line (from delivery.carrier.file)
        line.product_code = carrier.product_code or ''
        line.exped_trading_name = carrier.expeditor_name
        line.record_type = 'EXP'
        # Information from picking
        line.parcel_reference = picking.name
        line.exped_date = '%s%s%s' % (
            date_done[:4],
            date_done[5:7],
            date_done[8:10]
        )
        partner = picking.partner_id
        if partner:
            title = 0
            busi_name = ''
            # To find the partner's first name and last name, we split the
            # complete name of the partner. First string is considered first
            # name
            if partner.is_company:
                busi_name = partner.company or ''
                partner_name = partner.name
                partner_first_name = ''
            else:
                busi_name = partner.company or ''
                split_name = partner.name.split(' ', 1)
                if len(split_name) > 1:
                    partner_first_name = split_name[0]
                    partner_name = split_name[1]
                else:
                    partner_first_name = ''
                    partner_name = partner.name
                shortcut = partner.title and\
                    partner.title.shortcut.lower() or False
                if shortcut:
                    if shortcut in [part_title.lower() for part_title in MR]:
                        title = 2
                    elif shortcut in [part_title.lower() for part_title
                                      in MME]:
                        title = 3
                    elif shortcut in [part_title.lower() for part_title
                                      in MLLE]:
                        title = 4
            line.recipient_title = title
            line.recipient_busi_name = busi_name
            line.address_1 = ''
            line.address_2 = partner.street2 or ''
            line.address_3 = partner.street or ''
            line.address_4 = ''
            line.recipient_zip = partner.zip or ''
            if partner.city:
                city = unidecode(partner.city.upper())
            else:
                city = ''
            line.recipient_town = city
            line.recipient_name = partner_name or ''
            line.recipient_first_name = partner_first_name
            line.recipient_country_code = partner.country_id and \
                partner.country_id.code or ''

            line.phone_nb = partner.phone or ''
            line.recipient_mail = partner.email or ''
            line.recipient_mobile = partner.mobile or partner.phone or ''
            line.parcel_point = partner.mag_chronorelais_code or ''
            line.exped_trading_name = carrier.expeditor_name or ''

        sale = picking.sale_id
        if sale:
            line.delivery_instructions = 'COMMANDE : %s %s/%s' % (
                sale.name,
                package_nb,
                picking.number_of_packages or 1,
            )
            line.order_nb = sale.name
        line.weight = str(int((picking.weight or 0.500) * 1000)).rjust(15, '0')
        return line

    def rows(self):
        """
        Returns the rows to create in the file for a picking

        :param browse_record picking: the picking for which we generate
                                      a row in the file
        :param browse_record configuration: configuration of the
                                            file to generate
        :return: list of rows
        """
        lines = []
        line_values = self._line()
        last_position = 3
        for field_def in line_values.fields:
            if isinstance(getattr(line_values, field_def[0]), (int, float)):
                value = str(getattr(line_values, field_def[0]))
            else:
                value = u''.join(getattr(line_values, field_def[0]))
            if not value and field_def[0] in REQUIRED_FIELDS.keys():
                raise orm.except_orm(_("Error"),
                                     _("The field '%s' is required to print "
                                       " Colissimo labels") % REQUIRED_FIELDS[
                                         field_def[0]])
            width = field_def[1][0]
            position = field_def[1][1]
            len_diff = (position - last_position)
            if len_diff > 0:
                lines.append(u'%*s' % (len_diff, ''))
            lines.append(u'%-*.*s' % (width, width, value))
            last_position = position + width
        line = u''.join(lines)
        return [[line]]


class ColissimoFileGenerator(CarrierFileGenerator):

    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'colissimo'

    def _get_rows(self, picking, configuration, package_nb):
        gen = ColissimoRows(picking, configuration, package_nb)
        return gen.rows()

    def _write_rows(self, file_handle, rows, configuration):
        """
        Write the rows in the file (file_handle)

        :param StringIO file_handle: file to write in
        :param rows: rows to write in the file
        :param browse_record configuration: configuration of the
                                            file to generate
        :return: the file_handle as StringIO with the rows written in it
        """
        writer = UnicodeWriter(file_handle)
        writer.writerows(rows)
        return file_handle

    def generate_files(self, pickings, configuration):
        """
        Forbid to group pickings printing with the carrier type 'colissimo'
        """
        if configuration.group_pickings:
            if configuration.type == 'colissimo':
                raise orm.except_orm(_("Error"),
                                     _("You can't group pickings with carrier "
                                       "type 'colissimo' because we need one "
                                       "file per package"))
            return self._generate_files_grouped(pickings, configuration)
        else:
            return self._generate_files_single(pickings, configuration)

    def _generate_files_single(self, pickings, configuration):
        """
        Create one file per picking package
        """
        files = []
        for picking in pickings:
            total_packages = picking.number_of_packages or 1
            for x in xrange(1, total_packages + 1):
                filename = self._get_filename_single(picking, configuration)
                filename = filename % (x)
                filename = self.sanitize_filename(filename)
                rows = self._get_rows(picking, configuration, x)
                file_content = self._get_file(rows, configuration)
                files.append((filename, file_content, [picking.id]))
        return files

    def _get_filename_single(self, picking, configuration, extension='txt'):
        """
        No date for colissimo files
        """
        return "%s_%s.%s" % (picking.name, '%s', extension)
