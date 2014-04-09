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
import logging

from openerp.addons.magentoerpconnect.partner import (
    AddressImportMapper,
)
from .backend import magento_debonix

_logger = logging.getLogger(__name__)


@magento_debonix
class DebonixAddressImportMapper(AddressImportMapper):
    _model_name = 'magento.address'

    direct = (AddressImportMapper.direct +
              [('w_relay_point_code', 'mag_chronorelais_code'),
               ('company', 'mag_chronorelais_company'),
               ]
              )
