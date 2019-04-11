#  Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.http import request


class DisableWebsiteInfoController(Website):
    @http.route(auth="user")
    def website_info(self):
        return request.not_found()
