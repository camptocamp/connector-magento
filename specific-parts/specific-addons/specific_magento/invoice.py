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


from openerp.addons.magentoerpconnect import invoice
from openerp.addons.connector_ecommerce.event import (on_invoice_paid,
                                                      on_invoice_validated)


# Switch off the creation of binding for the invoice,
# debonix doesn't want to export invoices because they are
# always created on Magento before the import of the sales orders.
# If a magento.account.invoice binding record is created manually,
# it will still be exported though.
on_invoice_paid.unsubscribe(invoice.invoice_create_bindings)
on_invoice_validated.unsubscribe(invoice.invoice_create_bindings)
