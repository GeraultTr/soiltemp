
# -*- coding: latin-1 -*-
# This file has been generated at Thu Jun 12 09:53:31 2025

from openalea.core import *


__name__ = '__my_package__'

__editable__ = True
__version__ = ''
__license__ = ''
__authors__ = ''
__institutes__ = ''
__description__ = ''
__url__ = ''
__icon__ = ''
__alias__ = []


__all__ = ['__my_package___add_add']



__my_package___add_add = Factory(name='add',
                authors=' (wralea authors)',
                description='add two umbers',
                category='demo',
                nodemodule='__my_package__.add',
                nodeclass='add',
                inputs=[{'name': 'a', 'interface': IFloat, 'value': 0.0, 'desc': ''}, {'name': 'b', 'interface': IFloat, 'value': 0.0, 'desc': ''}],
                outputs=[{'name': 'sum', 'interface': None, 'desc': ''}],
                widgetmodule=None,
                widgetclass=None,
               )




