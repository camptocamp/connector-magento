# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Charbel Jacquin (Camptocamp)
#    Copyright 2015 Camptocamp SA
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
{'name': 'EDIFACT messages from purchase orders',
 'summary': 'Generate EDIFACT files on purchase order approval (sort of)',
 'version': '0.3',
 'author': 'Camptocamp',
 'maintainter': 'Camptocamp',
 'category': 'Purchase',
 'depends': ['purchase',
             'stockit_synchro',
             'delivery',],
 'description': """

Generate EDIFACT messages from purchase_orders
==============================================

Ce module implémente le format du pivot de commande e-commerce utilisé par
la société Debonix.

Ce format de commande est pris en charge par la plupart des filiales de Debonix
(hormis quelques exotiques) et il est compatible avec les deux principaux
systèmes d’information utilisés : Easy et Emeraude.

Note : Un compte client doit être crée sur le système d’information pour que
la commande puisse être intégrée.

Les fichiers pivots sont déposés dans un sas FTP pour être routé
vers les filiales souhaitées (TODO).

""",
 'website': 'http://www.camptocamp.com',
 'data': ['purchase_edi_view.xml',
          'purchase_edi_data.xml',
          'delivery_view.xml'],
 'tests': [],
 'installable': True,
 'auto_install': False,
 'license': 'AGPL-3',
 'application': False,
 }
