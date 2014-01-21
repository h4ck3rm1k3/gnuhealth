# -*- coding: utf-8 -*-
##############################################################################
#
#    GNU Health: The Free Health and Hospital Information System
#    Copyright (C) 2008-2014 Luis Falcon <lfalcon@gnusolidario.org>
#    Copyright (C) 2011-2014 GNU Solidario <health@gnusolidario.org>
#
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
import datetime
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Not, Bool
from trytond.pool import Pool
from trytond.transaction import Transaction


__all__ = ['PatientPregnancy', 'PrenatalEvaluation', 'PuerperiumMonitor',
    'Perinatal', 'PerinatalMonitor', 'GnuHealthPatient',
    'PatientMenstrualHistory', 'PatientMammographyHistory',
    'PatientPAPHistory', 'PatientColposcopyHistory']


class PatientPregnancy(ModelSQL, ModelView):
    'Patient Pregnancy'
    __name__ = 'gnuhealth.patient.pregnancy'

    name = fields.Many2One('gnuhealth.patient', 'Patient ID')
    gravida = fields.Integer('Pregnancy #', required=True)
    warning = fields.Boolean('Warn', help='Check this box if this is pregancy'
        ' is or was NOT normal')
    lmp = fields.Date('LMP', help="Last Menstrual Period", required=True)
    pdd = fields.Function(fields.Date('Pregnancy Due Date'),
        'get_pregnancy_data')
    prenatal_evaluations = fields.One2Many(
        'gnuhealth.patient.prenatal.evaluation', 'name',
        'Prenatal Evaluations')
    perinatal = fields.One2Many('gnuhealth.perinatal', 'name',
        'Perinatal Info')
    puerperium_monitor = fields.One2Many('gnuhealth.puerperium.monitor',
        'name', 'Puerperium monitor')
    current_pregnancy = fields.Boolean('Current Pregnancy', help='This field'
        ' marks the current pregnancy')
    fetuses = fields.Integer('Fetuses', required=True)
    monozygotic = fields.Boolean('Monozygotic')
    pregnancy_end_result = fields.Selection([
        (None, ''),
        ('live_birth', 'Live birth'),
        ('abortion', 'Abortion'),
        ('stillbirth', 'Stillbirth'),
        ('status_unknown', 'Status unknown'),
        ], 'Result', sort=False,
            states={
            'invisible': Bool(Eval('current_pregnancy')),
            'required': Not(Bool(Eval('current_pregnancy'))),
            })
    pregnancy_end_date = fields.DateTime('End of Pregnancy',
        states={
            'invisible': Bool(Eval('current_pregnancy')),
            'required': Not(Bool(Eval('current_pregnancy'))),
            })
    pregnancy_end_age = fields.Function(fields.Char('Weeks', help='Weeks at'
        ' the end of pregnancy'), 'get_pregnancy_data')
    iugr = fields.Selection([
        (None, ''),
        ('symmetric', 'Symmetric'),
        ('assymetric', 'Assymetric'),
        ], 'IUGR', sort=False)

    @classmethod
    def __setup__(cls):
        super(PatientPregnancy, cls).__setup__()
        cls._sql_constraints = [
            ('gravida_uniq', 'UNIQUE(name,gravida)', 'The pregancy number must'
                ' be unique for this patient !'),
        ]
        cls._error_messages.update({
            'patient_already_pregnant': 'Our records indicate that the patient'
                ' is already pregnant !'})

    @classmethod
    def validate(cls, pregnancies):
        super(PatientPregnancy, cls).validate(pregnancies)
        for pregnancy in pregnancies:
            pregnancy.check_patient_current_pregnancy()

    def check_patient_current_pregnancy(self):
        ''' Check for only one current pregnancy in the patient '''
        cursor = Transaction().cursor
        cursor.execute("SELECT count(name) "
            "FROM " + self._table + "  \
            WHERE (name = %s AND current_pregnancy)",
            (str(self.name.id),))
        if cursor.fetchone()[0] > 1:
            self.raise_user_error('patient_already_pregnant')

    @staticmethod
    def default_current_pregnancy():
        return True

    def get_pregnancy_data(self, name):
        if name == 'pdd':
            return self.lmp + datetime.timedelta(days=280)
        if name == 'pregnancy_end_age':
            if self.pregnancy_end_date:
                gestational_age = datetime.datetime.date(
                    self.pregnancy_end_date) - self.lmp
                return (gestational_age.days) / 7
            else:
                return 0


class PrenatalEvaluation(ModelSQL, ModelView):
    'Prenatal and Antenatal Evaluations'
    __name__ = 'gnuhealth.patient.prenatal.evaluation'

    name = fields.Many2One('gnuhealth.patient.pregnancy', 'Patient Pregnancy')
    evaluation = fields.Many2One('gnuhealth.patient.evaluation',
        'Patient Evaluation', readonly=True)
    evaluation_date = fields.DateTime('Date', required=True)
    gestational_weeks = fields.Function(fields.Integer('Gestational Weeks'),
        'get_patient_evaluation_data')
    gestational_days = fields.Function(fields.Integer('Gestational days'),
        'get_patient_evaluation_data')
    hypertension = fields.Boolean('Hypertension', help='Check this box if the'
        ' mother has hypertension')
    preeclampsia = fields.Boolean('Preeclampsia', help='Check this box if the'
        ' mother has pre-eclampsia')
    overweight = fields.Boolean('Overweight', help='Check this box if the'
        ' mother is overweight or obesity')
    diabetes = fields.Boolean('Diabetes', help='Check this box if the mother'
        ' has glucose intolerance or diabetes')
    invasive_placentation = fields.Selection([
        (None, ''),
        ('normal', 'Normal decidua'),
        ('accreta', 'Accreta'),
        ('increta', 'Increta'),
        ('percreta', 'Percreta'),
        ], 'Placentation', sort=False)
    placenta_previa = fields.Boolean('Placenta Previa')
    vasa_previa = fields.Boolean('Vasa Previa')
    fundal_height = fields.Integer('Fundal Height',
        help="Distance between the symphysis pubis and the uterine fundus "
        "(S-FD) in cm")
    fetus_heart_rate = fields.Integer('Fetus heart rate', help='Fetus heart'
        ' rate')
    efw = fields.Integer('EFW', help="Estimated Fetal Weight")
    fetal_bpd = fields.Integer('BPD', help="Fetal Biparietal Diameter")
    fetal_ac = fields.Integer('AC', help="Fetal Abdominal Circumference")
    fetal_hc = fields.Integer('HC', help="Fetal Head Circumference")
    fetal_fl = fields.Integer('FL', help="Fetal Femur Length")
    oligohydramnios = fields.Boolean('Oligohydramnios')
    polihydramnios = fields.Boolean('Polihydramnios')
    iugr = fields.Boolean('IUGR', help="Intra Uterine Growth Restriction")

    def get_patient_evaluation_data(self, name):
        if name == 'gestational_weeks':
            gestational_age = datetime.datetime.date(self.evaluation_date) - \
                self.name.lmp
            return (gestational_age.days) / 7
        if name == 'gestational_days':
            gestational_age = datetime.datetime.date(self.evaluation_date) - \
                self.name.lmp
            return gestational_age.days


class PuerperiumMonitor(ModelSQL, ModelView):
    'Puerperium Monitor'
    __name__ = 'gnuhealth.puerperium.monitor'

    name = fields.Many2One('gnuhealth.patient.pregnancy', 'Patient Pregnancy')
    date = fields.DateTime('Date and Time', required=True)
    # Deprecated in 1.6.4 All the clinical information will be taken at the
    # main evaluation.
    # systolic / diastolic / frequency / temperature
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    frequency = fields.Integer('Heart Frequency')
    temperature = fields.Float('Temperature')
    lochia_amount = fields.Selection([
        (None, ''),
        ('n', 'normal'),
        ('e', 'abundant'),
        ('h', 'hemorrhage'),
        ], 'Lochia amount', sort=False)
    lochia_color = fields.Selection([
        (None, ''),
        ('r', 'rubra'),
        ('s', 'serosa'),
        ('a', 'alba'),
        ], 'Lochia color', sort=False)
    lochia_odor = fields.Selection([
        (None, ''),
        ('n', 'normal'),
        ('o', 'offensive'),
        ], 'Lochia odor', sort=False)
    uterus_involution = fields.Integer('Fundal Height',
        help="Distance between the symphysis pubis and the uterine fundus "
        "(S-FD) in cm")


class Perinatal(ModelSQL, ModelView):
    'Perinatal Information'
    __name__ = 'gnuhealth.perinatal'

    name = fields.Many2One('gnuhealth.patient.pregnancy', 'Patient Pregnancy')
    admission_code = fields.Char('Code')
    # 1.6.4 Gravida number and abortion information go now in the pregnancy
    # header. It will be calculated as a function if needed
    gravida_number = fields.Integer('Gravida #')
    # Deprecated. Use End of Pregnancy as a general concept in the pregnancy
    # model
    # Abortion / Stillbirth / Live Birth
    abortion = fields.Boolean('Abortion')
    stillbirth = fields.Boolean('Stillbirth')
    admission_date = fields.DateTime('Admission',
        help="Date when she was admitted to give birth", required=True)
    # Prenatal evaluations deprecated in 1.6.4. Will be computed automatically
    prenatal_evaluations = fields.Integer('Prenatal evaluations',
        help="Number of visits to the doctor during pregnancy")
    start_labor_mode = fields.Selection([
        (None, ''),
        ('v', 'Vaginal - Spontaneous'),
        ('ve', 'Vaginal - Vacuum Extraction'),
        ('vf', 'Vaginal - Forceps Extraction'),
        ('c', 'C-section'),
        ], 'Delivery mode', sort=False)
    gestational_weeks = fields.Function(fields.Integer('Gestational wks'),
        'get_perinatal_information')
    gestational_days = fields.Integer('Days')
    fetus_presentation = fields.Selection([
        (None, ''),
        ('cephalic', 'Cephalic'),
        ('breech', 'Breech'),
        ('shoulder', 'Shoulder'),
        ], 'Fetus Presentation', sort=False)
    dystocia = fields.Boolean('Dystocia')
    placenta_incomplete = fields.Boolean('Incomplete',
        help='Incomplete Placenta')
    placenta_retained = fields.Boolean('Retained', help='Retained Placenta')
    abruptio_placentae = fields.Boolean('Abruptio Placentae',
        help='Abruptio Placentae')
    episiotomy = fields.Boolean('Episiotomy')
    #Vaginal tearing and forceps variables are deprecated in 1.6.4.
    #They are included in laceration and delivery mode respectively
    vaginal_tearing = fields.Boolean('Vaginal tearing')
    forceps = fields.Boolean('Forceps')
    monitoring = fields.One2Many('gnuhealth.perinatal.monitor', 'name',
        'Monitors')
    laceration = fields.Selection([
        (None, ''),
        ('perineal', 'Perineal'),
        ('vaginal', 'Vaginal'),
        ('cervical', 'Cervical'),
        ('broad_ligament', 'Broad Ligament'),
        ('vulvar', 'Vulvar'),
        ('rectal', 'Rectal'),
        ('bladder', 'Bladder'),
        ('urethral', 'Urethral'),
        ], 'Lacerations', sort=False)
    hematoma = fields.Selection([
        (None, ''),
        ('vaginal', 'Vaginal'),
        ('vulvar', 'Vulvar'),
        ('retroperitoneal', 'Retroperitoneal'),
        ], 'Hematoma', sort=False)
    # Deprecated in 1.6.4. Puerperium is now a separate entity from perinatal
    # and is included in the obstetric evaluation history
    # puerperium_monitor = fields.One2Many('gnuhealth.puerperium.monitor',
    #     'name', 'Puerperium monitor')
    # Deprecated in 1.6.4. The medication and procedures will be done in the
    # nursing and surgery modules
    medication = fields.One2Many('gnuhealth.patient.medication', 'name',
        'Medication and anesthesics')
    dismissed = fields.DateTime('Discharged')
    # Deprecated in 1.6.4 . Use the death information in the patient model
    # Date and cause of death
    place_of_death = fields.Selection([
        (None, ''),
        ('ho', 'Hospital'),
        ('dr', 'At the delivery room'),
        ('hh', 'in transit to the hospital'),
        ('th', 'Being transferred to other hospital'),
        ], 'Place of Death', help="Place where the mother died",
        states={'invisible': Not(Bool(Eval('mother_deceased')))},
        depends=['mother_deceased'], sort=False)
    mother_deceased = fields.Boolean('Maternal death',
        help="Mother died in the process")
    notes = fields.Text('Notes')

    def get_perinatal_information(self, name):
        if name == 'gestational_weeks':
            gestational_age = datetime.datetime.date(self.admission_date) - \
                self.name.lmp
            return (gestational_age.days) / 7


class PerinatalMonitor(ModelSQL, ModelView):
    'Perinatal Monitor'
    __name__ = 'gnuhealth.perinatal.monitor'

    name = fields.Many2One('gnuhealth.perinatal',
        'Patient Perinatal Evaluation')
    date = fields.DateTime('Date and Time')
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    contractions = fields.Integer('Contractions')
    frequency = fields.Integer('Mother\'s Heart Frequency')
    dilation = fields.Integer('Cervix dilation')
    f_frequency = fields.Integer('Fetus Heart Frequency')
    meconium = fields.Boolean('Meconium')
    bleeding = fields.Boolean('Bleeding')
    fundal_height = fields.Integer('Fundal Height')
    fetus_position = fields.Selection([
        (None, ''),
        ('o', 'Occiput / Cephalic Posterior'),
        ('fb', 'Frank Breech'),
        ('cb', 'Complete Breech'),
        ('t', 'Transverse Lie'),
        ('t', 'Footling Breech'),
        ], 'Fetus Position', sort=False)


class GnuHealthPatient(ModelSQL, ModelView):
    'Add to the Medical patient_data class (gnuhealth.patient) the ' \
    'gynecological and obstetric fields.'
    __name__ = 'gnuhealth.patient'

    currently_pregnant = fields.Function(fields.Boolean('Pregnant'),
        'get_pregnancy_info')
    fertile = fields.Boolean('Fertile',
        help="Check if patient is in fertile age")
    menarche = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    menopause = fields.Integer('Menopause age')
    mammography = fields.Boolean('Mammography',
        help="Check if the patient does periodic mammographys")
    mammography_last = fields.Date('Last mammography',
        help="Enter the date of the last mammography")
    breast_self_examination = fields.Boolean('Breast self-examination',
        help="Check if patient does and knows how to self examine her breasts")
    pap_test = fields.Boolean('PAP test',
        help="Check if patient does periodic cytologic pelvic smear screening")
    pap_test_last = fields.Date('Last PAP test',
        help="Enter the date of the last Papanicolau test")
    colposcopy = fields.Boolean('Colposcopy',
        help="Check if the patient has done a colposcopy exam")
    colposcopy_last = fields.Date('Last colposcopy',
        help="Enter the date of the last colposcopy")
    gravida = fields.Integer('Pregnancies', help="Number of pregnancies")
    premature = fields.Integer('Premature', help="Premature Deliveries")
    abortions = fields.Integer('Abortions')
    stillbirths = fields.Integer('Stillbirths')
    full_term = fields.Integer('Full Term', help="Full term pregnancies")
    # GPA Deprecated in 1.6.4. It will be used as a function or report from the
    # other fields
    #    gpa = fields.Char('GPA',
    #        help="Gravida, Para, Abortus Notation. For example G4P3A1 : 4 " \
    #        "Pregnancies, 3 viable and 1 abortion")
    # Deprecated. The born alive number will be calculated from pregnancies -
    # abortions - stillbirths
    #    born_alive = fields.Integer('Born Alive')
    # Deceased in 1st week or after 2nd weeks are deprecated since 1.6.4 .
    # The information will be retrieved from the neonatal or infant record
    #    deaths_1st_week = fields.Integer('Deceased during 1st week',
    #        help="Number of babies that die in the first week")
    #    deaths_2nd_week = fields.Integer('Deceased after 2nd week',
    #        help="Number of babies that die after the second week")
    # Perinatal Deprecated since 1.6.4 - Included in the obstetric history
    #    perinatal = fields.One2Many('gnuhealth.perinatal', 'name',
    #        'Perinatal Info')
    menstrual_history = fields.One2Many('gnuhealth.patient.menstrual_history',
        'name', 'Menstrual History')
    mammography_history = fields.One2Many(
        'gnuhealth.patient.mammography_history', 'name', 'Mammography History')
    pap_history = fields.One2Many('gnuhealth.patient.pap_history', 'name',
        'PAP smear History')
    colposcopy_history = fields.One2Many(
        'gnuhealth.patient.colposcopy_history', 'name', 'Colposcopy History')
    pregnancy_history = fields.One2Many('gnuhealth.patient.pregnancy', 'name',
        'Pregnancies')

    def get_pregnancy_info(self, name):
        if name == 'currently_pregnant':
            for pregnancy_history in self.pregnancy_history:
                if pregnancy_history.current_pregnancy:
                    return True
        return False


class PatientMenstrualHistory(ModelSQL, ModelView):
    'Menstrual History'
    __name__ = 'gnuhealth.patient.menstrual_history'

    name = fields.Many2One('gnuhealth.patient', 'Patient', readonly=True,
        required=True)
    evaluation = fields.Many2One('gnuhealth.patient.evaluation', 'Evaluation',
        domain=[('patient', '=', Eval('name'))])
    evaluation_date = fields.Date('Date', help="Evaluation Date",
        required=True)
    lmp = fields.Date('LMP', help="Last Menstrual Period", required=True)
    lmp_length = fields.Integer('Length', required=True)
    is_regular = fields.Boolean('Regular')
    dysmenorrhea = fields.Boolean('Dysmenorrhea')
    frequency = fields.Selection([
        ('amenorrhea', 'amenorrhea'),
        ('oligomenorrhea', 'oligomenorrhea'),
        ('eumenorrhea', 'eumenorrhea'),
        ('polymenorrhea', 'polymenorrhea'),
        ], 'frequency', sort=False)
    volume = fields.Selection([
        ('hypomenorrhea', 'hypomenorrhea'),
        ('normal', 'normal'),
        ('menorrhagia', 'menorrhagia'),
        ], 'volume', sort=False)

    @staticmethod
    def default_evaluation_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_frequency():
        return 'eumenorrhea'

    @staticmethod
    def default_volume():
        return 'normal'


class PatientMammographyHistory(ModelSQL, ModelView):
    'Mammography History'
    __name__ = 'gnuhealth.patient.mammography_history'

    name = fields.Many2One('gnuhealth.patient', 'Patient', readonly=True,
        required=True)
    evaluation = fields.Many2One('gnuhealth.patient.evaluation', 'Evaluation',
        domain=[('patient', '=', Eval('name'))])
    evaluation_date = fields.Date('Date', help=" Date")
    last_mammography = fields.Date('Date', help="Last Mammography",
        required=True)
    result = fields.Selection([
        (None, ''),
        ('normal', 'normal'),
        ('abnormal', 'abnormal'),
        ], 'result', help="Please check the lab test results if the module is \
            installed", sort=False)
    comments = fields.Char('Remarks')

    @staticmethod
    def default_evaluation_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_last_mammography():
        return Pool().get('ir.date').today()


class PatientPAPHistory(ModelSQL, ModelView):
    'PAP Test History'
    __name__ = 'gnuhealth.patient.pap_history'

    name = fields.Many2One('gnuhealth.patient', 'Patient', readonly=True,
        required=True)
    evaluation = fields.Many2One('gnuhealth.patient.evaluation', 'Evaluation',
        domain=[('patient', '=', Eval('name'))])
    evaluation_date = fields.Date('Date', help=" Date")
    last_pap = fields.Date('Date', help="Last Papanicolau", required=True)
    result = fields.Selection([
        (None, ''),
        ('negative', 'Negative'),
        ('c1', 'ASC-US'),
        ('c2', 'ASC-H'),
        ('g1', 'ASG'),
        ('c3', 'LSIL'),
        ('c4', 'HSIL'),
        ('g4', 'AIS'),
        ], 'result', help="Please check the lab results if the module is \
            installed", sort=False)
    comments = fields.Char('Remarks')

    @staticmethod
    def default_evaluation_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_last_pap():
        return Pool().get('ir.date').today()


class PatientColposcopyHistory(ModelSQL, ModelView):
    'Colposcopy History'
    __name__ = 'gnuhealth.patient.colposcopy_history'

    name = fields.Many2One('gnuhealth.patient', 'Patient', readonly=True,
        required=True)
    evaluation = fields.Many2One('gnuhealth.patient.evaluation', 'Evaluation',
        domain=[('patient', '=', Eval('name'))])
    evaluation_date = fields.Date('Date', help=" Date")
    last_colposcopy = fields.Date('Date', help="Last colposcopy",
        required=True)
    result = fields.Selection([
        (None, ''),
        ('normal', 'normal'),
        ('abnormal', 'abnormal'),
        ], 'result', help="Please check the lab test results if the module is \
            installed", sort=False)
    comments = fields.Char('Remarks')

    @staticmethod
    def default_evaluation_date():
        return Pool().get('ir.date').today()

    @staticmethod
    def default_last_colposcopy():
        return Pool().get('ir.date').today()
