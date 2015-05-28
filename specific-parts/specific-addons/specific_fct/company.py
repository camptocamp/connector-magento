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
from openerp.osv import fields, orm
try:
    from server_environment import serv_config
except ImportError:
    logging.getLogger('openerp.module').warning(
        'server_environment not available in addons path. '
        'specific_fct will not be usable'
    )

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

class res_company(orm.Model):
    _inherit = 'res.company'

    def _get_environment_config_by_id(self, cr, uid, ids, field_names,
                                      arg, context=None):
        values = {}
        _logger.debug('GECBI %r [%r]:', field_names, arg)
        for company in self.browse(cr, uid, ids, context=context):
            values[company.id] = {}
            for field_name in field_names:
                section_name = '.'.join((self._name.replace('.', '_'),
                                         str(company.id)))
                try:
                    value = serv_config.get(section_name, field_name)
                    if field_name in ('sftp_invoice_port', 'edifact_purchase_port'):
                        value = int(value) if value else 0
                except:
                    _logger.exception('error trying to read field %s '
                                      'in section %s', field_name,
                                      section_name)
                    value = False
                values[company.id][field_name] = value
        return values

    _columns = {
        'sftp_invoice_host': fields.function(
            _get_environment_config_by_id,
            string='Host',
            type='char',
            multi='server_env'),
        'sftp_invoice_port': fields.function(
            _get_environment_config_by_id,
            string='Port',
            type='integer',
            multi='server_env'),
        'sftp_invoice_user': fields.function(
            _get_environment_config_by_id,
            string='Username',
            type='char',
            multi='server_env'),
        'sftp_invoice_path': fields.function(
            _get_environment_config_by_id,
            string='Path',
            type='char',
            multi='server_env'),

        'edifact_purchase_host': fields.function(
            _get_environment_config_by_id,
            string='Host',
            type='char',
            multi='server_env'),
        'edifact_purchase_user': fields.function(
            _get_environment_config_by_id,
            string='Username',
            type='char',
            multi='server_env'),
        'edifact_purchase_password': fields.function(
            _get_environment_config_by_id,
            string='Password',
            type='char',
            multi='server_env'),
        'edifact_purchase_path': fields.function(
            _get_environment_config_by_id,
            string="Path",
            type='char',
            multi='server_env')
        }
