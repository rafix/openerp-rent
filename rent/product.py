# -*- encoding: utf-8 -*-
#
# OpenERP Rent - A rent module for OpenERP 6
# Copyright (C) 2010-Today Thibaut DIRLIK <thibaut.dirlik@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import logging

from osv import osv, fields
from tools.translate import _
from openlib import Searcher

_logger = logging.getLogger('rent')

class Product(osv.osv):

    def check_rent_price(self, cursor, user_id, ids, context=None):

        """
        We check that the rent price is neither empty or 0 if the product can be rent.
        """

        products = self.browse(cursor, user_id, ids, context=context)

        for product in products:
            if product.can_be_rent:
                if not product.rent_price or product.rent_price <= 0:
                    return False
        return True

    def default_price_unity(self, cr, uid, context=None):

        """
        Returns the default price unity (the first in the list).
        """

        category_id = self.default_price_unity_category(cr, uid, context=context)
        if not category_id:
            _logger.error("Your company isn't configured correctly. Please define 'rent_unity_category'.")
        else:
            unity = Searcher(cr, uid, 'product.uom', context=context, category_id=category_id).browse_one()
            return unity.id if unity else False

    def default_price_unity_category(self, cr, uid, context=None):

        """
        Returns the price unity category of the user's company.
        """

        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        return self.pool.get('res.company').browse(cr, uid, company_id, context=context).rent_unity_category.id

    _name = 'product.product'
    _inherit = 'product.product'

    _columns = {
        'can_be_rent' : fields.boolean('Can be rented', help='Enable this if you want to rent this product.'),
        'rent_price' : fields.float('Rent price', help=
            'The price is expressed for the duration unity defined in the company configuration.'),
        'rent_price_unity' : fields.many2one('product.uom', 'Rent Price Unity',
            help='Rent duration unity in which the price is defined.', required=True),
        'rent_price_unity_category' : fields.many2one('product.uom.categ', readonly=True, required=True)
    }

    _defaults = {
        'can_be_rent' : False,
        'rent_price' : 1.0,
        'rent_price_unity' : default_price_unity,
        'rent_price_unity_category' : default_price_unity_category,
    }

    _constraints = [(check_rent_price, _('The Rent price must be a positive value.'), ['rent_price']),]

Product()
