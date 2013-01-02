# -*- coding: utf-8 -*-
##############################################################################
#
#    GNU Health: The Free Health and Hospital Information System
#    Copyright (C) 2008-2013  Luis Falcon <lfalcon@gnusolidario.org>
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
from trytond.model import ModelView
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.transaction import Transaction
from trytond.pool import Pool


__all__ = ['CreateLabTestOrderInit', 'CreateLabTestOrder']


class CreateLabTestOrderInit(ModelView):
    'Create Test Report Init'
    __name__ = 'gnuhealth.lab.test.create.init'


class CreateLabTestOrder(Wizard):
    'Create Lab Test Report'
    __name__ = 'gnuhealth.lab.test.create'

    start = StateView('gnuhealth.lab.test.create.init',
        'health_lab.view_lab_make_test', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Create Test Order', 'create_lab_test', 'tryton-ok', True),
            ])

    create_lab_test = StateTransition()


    def transition_create_lab_test(self):
        TestRequest = Pool().get('gnuhealth.patient.lab.test')
        Lab = Pool().get('gnuhealth.lab')

        test_report_data = {}
        test_cases = []

        tests = TestRequest.browse(Transaction().context.get('active_ids'))

        for lab_test_order in tests:

            if lab_test_order.state == 'ordered':
                raise Exception('The Lab test order is already created.')

            test_report_data['test'] = lab_test_order.name.id
            test_report_data['patient'] = lab_test_order.patient_id.id
            test_report_data['requestor'] = lab_test_order.doctor_id.id
            test_report_data['date_requested'] = lab_test_order.date

            for critearea in lab_test_order.name.critearea:
                test_cases.append(('create', {
                        'name': critearea.name,
                        'sequence': critearea.sequence,
                        'lower_limit': critearea.lower_limit,
                        'upper_limit': critearea.upper_limit,
                        'normal_range': critearea.normal_range,
                        'units': critearea.units and critearea.units.id,
                    }))
            test_report_data['critearea'] = test_cases
            Lab.create(test_report_data)
            TestRequest.write([lab_test_order], {'state': 'ordered'})

        return 'end'

