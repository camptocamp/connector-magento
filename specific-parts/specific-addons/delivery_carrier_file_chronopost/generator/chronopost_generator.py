# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2012 Camptocamp SA
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

import csv

from openerp.addons.base_delivery_carrier_files.generator \
    import CarrierFileGenerator
from openerp.addons.base_delivery_carrier_files.generator import BaseLine
from openerp.addons.base_delivery_carrier_files.csv_writer \
    import UnicodeWriter


class ChronopostLine(BaseLine):
    fields = (('subaccount', 3),
              ('client_code', 15),
              ('name1', 35),
              ('name2', 35),
              ('street1', 35),
              ('street2', 35),
              ('zip', 5),
              ('city', 30),
              ('country', 2),
              ('phone', 20),
              ('email', 35),
              ('ref1', 20),
              ('ref2', 20),
              ('weight', 6),
              ('chrono_product', 3),
              ('saturday_delivery', 1),
              ('insurance_amount', 8),
              ('rep_amount', 8),
              ('customs_amount', 8),)


class ChronopostFileGenerator(CarrierFileGenerator):

    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'chronopost'

    def _get_rows(self, picking, configuration):
        """
        Returns the rows to create in the file for a picking

        :param browse_record picking: the picking for which we generate
                                      a row in the file
        :param browse_record configuration: configuration of the
                                            file to generate
        :return: list of rows
        """
        lines = []
        line = ChronopostLine()
        line.subaccount = configuration.subaccount_number
        line.chrono_product = configuration.chronopost_code
        line.saturday_delivery = configuration.saturday_delivery_code
        line.insurance_amount = configuration.chronopost_insurance or '0.0'

        address = picking.address_id
        if address:
            line.client_code = address.partner_id.id
            line.name1 = address.name
            line.street1 = address.street
            line.street2 = address.street2
            line.zip = address.zip
            line.city = address.city
            line.country = (address.country_id and
                            address.country_id.code or False)
            line.phone = address.phone
            line.email = address.email

        line.ref1 = picking.name
        line.ref2 = picking.sale_id and picking.sale_id.name or False
        line.weight = picking.weight or 0.5  # minimal weight
        line.rep_amount = "%.2f" % picking.cash_on_delivery_amount
        line.customs_amount = "%.2f" % picking.cash_on_delivery_amount_untaxed

        for x in range(picking.number_of_packages or 1):
            lines.append(line.get_fields())

        return lines

    def _write_rows(self, file_handle, rows, configuration):
        """
        Write the rows in the file (file_handle)

        :param StringIO file_handle: file to write in
        :param rows: rows to write in the file
        :param browse_record configuration: configuration of the
                                            file to generate
        :return: the file_handle as StringIO with the rows written in it
        """
        writer = UnicodeWriter(file_handle, delimiter=';', quotechar='"',
                               lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
        return file_handle
