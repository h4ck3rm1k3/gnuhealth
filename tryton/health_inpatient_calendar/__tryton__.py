# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011  Sebastián Marró <smarro@thymbra.com>
#    $Id$
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
    'name': 'GNU Health: Inpatient Calendar',
    'version': '1.4.3',
    'author': 'GNU Solidario',
    'website': 'http://health.gnu.org',
    'depends': [
        'health_inpatient',
        'calendar',
    ],
    'xml': [
        'health_inpatient_calendar_view.xml',
    ],
    'name_es_ES': 'GNU Health : Calendario para Hospitalización',
#    'translation': [
#        'locale/es_ES.po',
#    ],
    'description': ''' 
        This module add functionality to connect with a CalDAV client.
        ''',
    'description_es_ES': ''' 
        Este módulo añade funcionalidad para conectar con un cliente CalDAV, 
        ''',
}
