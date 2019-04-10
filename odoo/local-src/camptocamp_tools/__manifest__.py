# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{'name': 'Camptocamp tools',
 'description': "Camptocamp tools and version controller.",
 'version': '12.0.1.0.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Others',
 'depends': [
     'base',
     'web',
 ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'templates/camptocamp_version_template.xml',
     'views/camptocamp_version.xml'
 ],
 'installable': True,
 'auto_install': True,
 }
