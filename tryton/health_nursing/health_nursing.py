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
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields
from datetime import datetime
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.pyson import Eval


__all__ = ['GnuHealthSequences', 'PatientRounding', 'RoundingProcedure',
    'PatientAmbulatoryCare', 'AmbulatoryCareProcedure']


class GnuHealthSequences(ModelSingleton, ModelSQL, ModelView):
    "Standard Sequences for GNU Health"

    _description = __doc__
    _name = "gnuhealth.sequences"

    ambulatory_care_sequence = fields.Property(fields.Many2One('ir.sequence',
        'Health Ambulatory Care', domain=[
            ('code', '=', 'gnuhealth.ambulatory_care')
        ], required=True))


# Class : PatientRounding
# Assess the patient and evironment periodically
# Usually done by nurses

class PatientRounding(ModelSQL, ModelView):
    'Patient Rounding'
    _name = 'gnuhealth.patient.rounding'
    _description = __doc__

    name = fields.Many2One('gnuhealth.inpatient.registration', 'Registration Code', required=True)

    health_professional = fields.Many2One('gnuhealth.physician', 'Health Professional', readonly=True)

    evaluation_start = fields.DateTime('Start', required=True)
    evaluation_end = fields.DateTime('End', required=True)

    environmental_assessment = fields.Char('Environment', help="Environment" \
        " assessment . State any disorder in the room.")

    # The 6 P's of rounding
    pain = fields.Boolean('Pain', help="Check if the patient is in pain")
    pain_level = fields.Integer('Pain', help="Enter the pain level, from 1 to 10")
    potty = fields.Boolean ('Potty', help="Check if the patient needs to urinate / defecate")
    position = fields.Boolean ('Position', help="Check if the patient needs to be repositioned or is unconfortable")
    proximity = fields.Boolean ('Proximity', help="Check if personal items, water, alarm, ... are not in easy reach")
    pump = fields.Boolean ('Pumps', help="Check if there is any issues with the pumps - IVs ... ")
    personal_needs = fields.Boolean ('Personal needs',help="Check if the patient requests anything")

    # Vital Signs
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    bpm = fields.Integer('Heart Rate',
        help='Heart rate expressed in beats per minute')
    respiratory_rate = fields.Integer('Respiratory Rate',
        help='Respiratory rate expressed in breaths per minute')
    osat = fields.Integer('Oxygen Saturation',
        help='Oxygen Saturation(arterial).')
    temperature = fields.Float('Temperature',
        help='Temperature in celsius')


    #Glycemia
    glycemia = fields.Integer('Glycemia', help='Blood Glucose level')

    depression = fields.Boolean ('Depression signs',help="Check this if the patient shows signs of depression")

    evolution = fields.Selection([
        ('n', 'Status Quo'),
        ('i', 'Improving'),
        ('w', 'Worsening'),
        ], 'Evolution', required=True, help="Check your judgement of current patient condition", sort=False)

    round_summary = fields.Text('Round Summary')

    warning = fields.Boolean('Warning', help="Check this box to alert the supervisor about this patient rounding" \
        ". It will be shown in red in the rounding list")

    procedures = fields.One2Many('gnuhealth.rounding_procedure', 'name', 'Procedures',
        help="List of the procedures in this rounding. Please enter the first " \
        "one as the main procedure")

    def default_health_professional(self):
        cursor = Transaction().cursor
        user_obj = Pool().get('res.user')
        user = user_obj.browse(Transaction().user)
        login_user_id = int(user.id)
        cursor.execute('SELECT id FROM party_party WHERE is_doctor=True AND \
            internal_user = %s LIMIT 1', (login_user_id,))
        partner_id = cursor.fetchone()
        if not partner_id:
            self.raise_user_error('No health professional associated to this \
                user')
        else:
            cursor = Transaction().cursor
            cursor.execute('SELECT id FROM gnuhealth_physician WHERE \
                name = %s LIMIT 1', (partner_id[0],))
            doctor_id = cursor.fetchone()

            return int(doctor_id[0])


    def default_evaluation_start(self):
        return datetime.now()


class RoundingProcedure(ModelSQL, ModelView):
    'Rounding - Procedure'
    _name = 'gnuhealth.rounding_procedure'
    _description = __doc__

    name = fields.Many2One('gnuhealth.patient.rounding', 'Rounding')
    procedure = fields.Many2One('gnuhealth.procedure', 'Code', required=True,
        select=True,
        help="Procedure Code, for example ICD-10-PCS Code 7-character string")
    notes = fields.Text('Notes')


class PatientAmbulatoryCare(ModelSQL, ModelView):
    'Patient Ambulatory Care'
    _name = 'gnuhealth.patient.ambulatory_care'
    _description = __doc__


    name = fields.Char('ID', readonly=True)
    patient = fields.Many2One ('gnuhealth.patient', 'Patient', required=True)
    base_condition = fields.Many2One ('gnuhealth.pathology', 'Base Condition')
    evaluation = fields.Many2One('gnuhealth.patient.evaluation', 'Related Evaluation', domain=[('patient', '=', Eval('patient'))])
    ordering_professional = fields.Many2One('gnuhealth.physician', 'Ordering Physician')
    health_professional = fields.Many2One('gnuhealth.physician', 'Health Professional', readonly=True)

    procedures = fields.One2Many('gnuhealth.ambulatory_care_procedure', 'name', 'Procedures',
        help="List of the procedures in this session. Please enter the first " \
        "one as the main procedure")


    session_number = fields.Integer('Session #', required=True)

    session_start = fields.DateTime('Start', required=True)

    # Vital Signs
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    bpm = fields.Integer('Heart Rate',
        help='Heart rate expressed in beats per minute')
    respiratory_rate = fields.Integer('Respiratory Rate',
        help='Respiratory rate expressed in breaths per minute')
    osat = fields.Integer('Oxygen Saturation',
        help='Oxygen Saturation(arterial).')
    temperature = fields.Float('Temperature',
        help='Temperature in celsius')

    warning = fields.Boolean('Warning', help="Check this box to alert the supervisor about this session" \
        ". It will be shown in red in the session list")

    #Glycemia
    glycemia = fields.Integer('Glycemia', help='Blood Glucose level')

    evolution = fields.Selection([
        ('initial', 'Initial'),
        ('n', 'Status Quo'),
        ('i', 'Improving'),
        ('w', 'Worsening'),
        ], 'Evolution', required=True, help="Check your judgement of current patient condition", sort=False)


    session_end = fields.DateTime('End', required=True)

    next_session = fields.DateTime('Next Session')

    session_notes = fields.Text('Notes', required=True)

    def create(self, values):
        sequence_obj = Pool().get('ir.sequence')
        config_obj = Pool().get('gnuhealth.sequences')

        values = values.copy()
        if not values.get('name'):
            config = config_obj.browse(1)
            values['name'] = sequence_obj.get_id(
            config.ambulatory_care_sequence.id)

        return super(PatientAmbulatoryCare, self).create(values)

    def default_health_professional(self):
        cursor = Transaction().cursor
        user_obj = Pool().get('res.user')
        user = user_obj.browse(Transaction().user)
        login_user_id = int(user.id)
        cursor.execute('SELECT id FROM party_party WHERE is_doctor=True AND \
            internal_user = %s LIMIT 1', (login_user_id,))
        partner_id = cursor.fetchone()
        if not partner_id:
            self.raise_user_error('No health professional associated to this \
                user')
        else:
            cursor = Transaction().cursor
            cursor.execute('SELECT id FROM gnuhealth_physician WHERE \
                name = %s LIMIT 1', (partner_id[0],))
            doctor_id = cursor.fetchone()

            return int(doctor_id[0])


    def default_session_start(self):
        return datetime.now()


class AmbulatoryCareProcedure(ModelSQL, ModelView):
    'Ambulatory Care Procedure'
    _name = 'gnuhealth.ambulatory_care_procedure'
    _description = __doc__

    name = fields.Many2One('gnuhealth.patient.ambulatory_care', 'Session')
    procedure = fields.Many2One('gnuhealth.procedure', 'Code', required=True,
        select=True,
        help="Procedure Code, for example ICD-10-PCS Code 7-character string")
    comments = fields.Char('Comments')
