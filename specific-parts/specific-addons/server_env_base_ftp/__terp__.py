# -*- coding: utf-8 -*-
##############################################################################
#
#    Author Guewen Baconnier. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Server configuration environment for base_ftp",
    "version": "1.0",
    "depends": ["base", 'server_environment', 'base_ftp'],
    "author": "Camptocamp",
    "description": """This module is based on the server_environment module to use files for configuration.
Thus we can have a different file for each environment (dev, staging, prod).
This module define the config variables for the base_ftp module.
    """,
    "website": "http://www.camptocamp.com",
    "category": "Tools",
    "init_xml": [],
    "demo_xml": [],
    "update_xml": [],
    "installable": True,
    "active": False,
}
