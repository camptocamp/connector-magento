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

import csv

from openerp.addons.base_delivery_carrier_files.generator \
    import CarrierFileGenerator
from openerp.addons.base_delivery_carrier_files.generator import BaseLine
from openerp.addons.base_delivery_carrier_files.csv_writer \
    import UnicodeWriter


class ColissimoLine(BaseLine):
    fields = (('record_type', 3),
              ('parcel_reference', 35),
              ('exped_date', 8),
              ('product_code', 4),
              ('recipient_name', 35),
              ('address_1', 35),
              ('address_2', 35),
              ('address_3', 35),
              ('recipient_zip', 9),
              ('recipient_town', 35),
              ('recipient_country_code', 3),
              ('delivery_instructions', 70),
              ('weight', 15),
              ('phone_nb', 25),
              ('recipient_mail', 75),
              ('address_4', 35),
              ('order_nb', 35),
              ('recipient_title', 1),
              ('recipient_first_name', 29),
              ('recipient_busi_name', 38),
              ('recipient_mobile', 10),
              ('parcel_point', 6),
              ('exped_trading_name', 38),)


class ColissimoRows(object):

    def __init__(self, picking, configuration):
        self.picking = picking
        self.configuration = configuration

    def _line(self):
        configuration = self.configuration
        picking = self.picking

        line = ColissimoLine()
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
        line.weight = 0.5  # minimal weight
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


class ColissimoFileGenerator(CarrierFileGenerator):

    @classmethod
    def carrier_for(cls, carrier_name):
        return carrier_name == 'colissimo'

    def _get_rows(self, picking, configuration):
        gen = ColissimoRows(picking, configuration)
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

