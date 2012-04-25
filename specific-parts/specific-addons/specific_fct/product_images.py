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

import os

from openerp.osv.orm import Model


class product_images(Model):

    _inherit = 'product.images'

    def _image_path(self, cr, uid, image, context=None):
        full_path = False
        local_media_repository = self.pool.get('res.company').\
             get_local_media_repository(cr, uid, context=context)
        if local_media_repository:
            full_path = os.path.join(
                local_media_repository,
                '%s%s' % (image.name or '', image.extention or ''))
        return full_path
