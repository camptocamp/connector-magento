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


class ChronopostRows(object):

    def __init__(self, picking, configuration):
        self.picking = picking
        self.configuration = configuration

    def _line(self):
        configuration = self.configuration
        picking = self.picking

        line = ChronopostLine()
        line.subaccount = configuration.subaccount_number
        line.chrono_product = configuration.chronopost_code
        line.saturday_delivery = configuration.saturday_delivery_code
        line.insurance_amount = configuration.chronopost_insurance or '0.0'

        address = picking.partner_id
        if address:
            if address.parent_id:
                line.client_code = address.parent_id.id
            else:
                line.client_code = address.id
            line.name1 = address.name

            if address.company:
                line.name2 = address.company
            else:
                if address.parent_id:
                    parent = address.parent_id
                    name = (address.name or '').strip().lower()
                    parent_name = (parent.name or '').strip().lower()
                    bindings = parent.magento_bind_ids
                    if (name != parent_name and
                        (not bindings or
                         any(bind.consider_as_company for bind in bindings))):
                        # probably a company name
                        line.name2 = parent.name

            line.street1 = address.street
            line.street2 = address.street2
            line.zip = address.zip
            line.city = address.city
            country = address.country_id.code if address.country_id else False
            line.country = country
            line.phone = picking.sms_phone
            line.email = address.email
            if not line.email and address.parent_id:
                line.email = address.parent_id.email

        line.ref1 = picking.name
        line.ref2 = picking.sale_id and picking.sale_id.name or False
        line.weight = picking.weight or 0.5  # minimal weight
        line.rep_amount = "%.2f" % picking.cash_on_delivery_amount
        line.customs_amount = "%.2f" % picking.cash_on_delivery_amount_untaxed
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
        line = self._line()
        lines = []
        # output as many lines as number of packages
        for x in xrange(self.picking.number_of_packages or 1):
            lines.append(line.get_fields())

        return lines


class ChronorelaisRows(ChronopostRows):

    def _line(self):
        line = super(ChronorelaisRows, self)._line()
        address = self.picking.partner_id
        line.ref1 = ''
        if address:
            # chrono relay's company
            line.name1 = address.mag_chronorelais_company
            # person's name who can withdraw the pack
            line.name2 = address.name
            line.ref1 = address.mag_chronorelais_code
        line.ref2 = self.picking.name
        return line


class ChronopostFileGenerator(CarrierFileGenerator):

    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'chronopost'

    def _get_rows(self, picking, configuration):
        gen = ChronopostRows(picking, configuration)
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
        writer = UnicodeWriter(file_handle, delimiter=';', quotechar='"',
                               lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
        return file_handle


class ChronorelaisFileGenerator(CarrierFileGenerator):

    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'chronorelais'

    def _get_rows(self, picking, configuration):
        gen = ChronorelaisRows(picking, configuration)
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
        writer = UnicodeWriter(file_handle, delimiter=';', quotechar='"',
                               lineterminator='\n', quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
        return file_handle
