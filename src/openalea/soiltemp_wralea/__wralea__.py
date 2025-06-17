
# -*- coding: latin-1 -*-
# This file has been generated at Tue Jun 17 11:14:47 2025

from openalea.core import *


__name__ = 'amei.soil_temperature.tutorial'

__editable__ = True
__version__ = '0.0.1'
__license__ = 'Cecill-C'
__authors__ = 'AMEI Consortium'
__institutes__ = 'INRIA/CIRAD/INRAE'
__description__ = 'Nodes for soil temperature models creation, edition and visualisation.'
__url__ = 'http://openalea.rtfd.io'
__icon__ = ''
__alias__ = []


__all__ = ['SoilTemperature']



SoilTemperature = CompositeNodeFactory(name='SoilTemperature',
                             description='Simulation of Soil Temperature Model',
                             category='soil',
                             doc='',
                             inputs=[],
                             outputs=[],
                             elt_factory={  2: ('amei.soil_temperature', 'config'),
   3: ('amei.soil_temperature', 'Models'),
   4: ('amei.soil_temperature', 'columns'),
   5: ('openalea.pylab.plotting', 'PyLabPlot')},
                             elt_connections={  4303796368: (2, 0, 3, 1),
   4303796400: (3, 0, 4, 0),
   4303796432: (4, 0, 5, 1),
   4303796464: (4, 1, 5, 2)},
                             elt_data={  2: {  'block': False,
         'caption': 'config',
         'delay': 0,
         'hide': True,
         'id': 2,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 3.1617236496814627,
         'posy': -4.075796678983966,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   3: {  'block': False,
         'caption': 'SiriusQuality',
         'delay': 0,
         'hide': True,
         'id': 3,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 3.1776591359573985,
         'posy': 34.34316220015495,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   4: {  'block': False,
         'caption': 'columns',
         'delay': 0,
         'hide': True,
         'id': 4,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 18.227681696375363,
         'posy': 87.12213963352292,
         'priority': 0,
         'use_user_color': False,
         'user_application': None,
         'user_color': None},
   5: {  'block': False,
         'caption': 'PyLabPlot',
         'delay': 0,
         'hide': True,
         'id': 5,
         'lazy': False,
         'port_hide_changed': set(),
         'posx': 14.03205299671022,
         'posy': 155.68237824093168,
         'priority': 0,
         'use_user_color': False,
         'user_application': True,
         'user_color': None},
   '__in__': {  'block': False,
                'caption': 'In',
                'delay': 0,
                'hide': True,
                'id': 0,
                'lazy': True,
                'port_hide_changed': set(),
                'posx': 0,
                'posy': 0,
                'priority': 0,
                'use_user_color': True,
                'user_application': None,
                'user_color': None},
   '__out__': {  'block': False,
                 'caption': 'Out',
                 'delay': 0,
                 'hide': True,
                 'id': 1,
                 'lazy': True,
                 'port_hide_changed': set(),
                 'posx': 0,
                 'posy': 0,
                 'priority': 0,
                 'use_user_color': True,
                 'user_application': None,
                 'user_color': None}},
                             elt_value={  2: [(0, "'Montpellier/FR'"), (1, "'SICL'"), (2, "' 0.25'"), (3, "' 2'")],
   3: [(0, "'SiriusQuality'"), (2, '298')],
   4: [(1, "'TSLD'"), (2, '1')],
   5: [  (0, 'None'),
         (3, "'point'"),
         (4, '8.0'),
         (5, "'solid'"),
         (6, "'magenta'"),
         (7, 'True'),
         (8, 'True'),
         (9, "{'label': None}"),
         (10, '1')],
   '__in__': [],
   '__out__': []},
                             elt_ad_hoc={  2: {'position': [3.1617236496814627, -4.075796678983966], 'userColor': None, 'useUserColor': False},
   3: {'position': [3.1776591359573985, 34.34316220015495], 'userColor': None, 'useUserColor': False},
   4: {'position': [18.227681696375363, 87.12213963352292], 'userColor': None, 'useUserColor': False},
   5: {'position': [14.03205299671022, 155.68237824093168], 'userColor': None, 'useUserColor': False},
   '__in__': {'position': [0, 0], 'userColor': None, 'useUserColor': True},
   '__out__': {'position': [0, 0], 'userColor': None, 'useUserColor': True}},
                             lazy=True,
                             eval_algo='LambdaEvaluation',
                             )




