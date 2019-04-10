# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
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

"""
Monkey patching Cursor to be able to write file on fs only once
the commit is completed. Thus in case of rollback we won't create
orphan files.
"""

from openerp.sql_db import Cursor


def add_transaction_action(cr, callback, *args):
    """ Queue file information to be written after commit """
    if not hasattr(cr, 'transaction_actions'):
        cr.transaction_actions = []
    cr.transaction_actions.append((callback, args))

Cursor.add_transaction_action = add_transaction_action


former_commit = Cursor.commit


def commit(self):
    """ Perform an SQL `COMMIT`
    With write of file after commit to ensure it
    is written only after commit. And won't be
    in case of rollback.
    """
    if not hasattr(self, 'transaction_actions'):
        self.transaction_actions = []
    res = former_commit(self)
    while self.transaction_actions:
        callback, args = self.transaction_actions.pop(0)
        callback(*args)
    return res

Cursor.commit = commit


former_rollback = Cursor.rollback


def rollback(self):
    """ Perform an SQL `ROLLBACK`
    Clean file queue for the rolled back cursor
    """
    self.transaction_actions = []
    return former_rollback(self)

Cursor.rollback = rollback
