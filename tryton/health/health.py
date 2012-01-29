# coding=utf-8

#    Copyright (C) 2008-2012 Luis Falcon <lfalcon@gnusolidario.org>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import time
import logging

from dateutil.relativedelta import relativedelta
from datetime import datetime

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.tools import safe_eval, datetime_strftime
from trytond.transaction import Transaction
from trytond.pyson import Eval, Not, Equal, If, In, Bool, Get, Or, And, \
        PYSONEncoder
from trytond.pool import Pool



class DrugDoseUnits(ModelSQL, ModelView):
    "Drug Dose Unit"
    _description = __doc__

    _name = "gnuhealth.dose.unit"
    name = fields.Char('Unit', required=True, select=True, translate=True)
    desc = fields.Char('Description', translate=True)

    def __init__(self):
        super(DrugDoseUnits, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Unit must be unique !')]

DrugDoseUnits()


class MedicationFrequency(ModelSQL, ModelView):
    "Medication Common Frequencies"
    _description = __doc__

    _name = "gnuhealth.medication.dosage"
    name = fields.Char('Frequency', required=True, select=True, translate=True,
        help='Common frequency name')
    code = fields.Char('Code',
        help='Dosage Code,for example: SNOMED 229798009 = 3 times per day')
    abbreviation = fields.Char('Abbreviation',
        help='Dosage abbreviation, such as tid in the US or tds in the UK')

    def __init__(self):
        super(MedicationFrequency, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Unit must be unique !')]

MedicationFrequency()


class DrugForm(ModelSQL, ModelView):
    "Drug Form"
    _description = __doc__

    _name = "gnuhealth.drug.form"
    name = fields.Char('Form', required=True, select=True, translate=True)
    code = fields.Char('Code')

    def __init__(self):
        super(DrugForm, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Unit must be unique !')]

DrugForm()


class DrugRoute(ModelSQL, ModelView):
    "Drug Administration Route"
    _description = __doc__

    _name = "gnuhealth.drug.route"
    name = fields.Char('Unit', required=True, select=True, translate=True)
    code = fields.Char('Code')

    def __init__(self):
        super(DrugRoute, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Name must be unique !')]

DrugRoute()


class Occupation(ModelSQL, ModelView):
    "Occupation"
    _description = __doc__

    _name = "gnuhealth.occupation"
    name = fields.Char('Name', required="1", translate=True)
    code = fields.Char('Code')

    def __init__(self):
        super(Occupation, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Name must be unique !')]

Occupation()


class Ethnicity(ModelSQL, ModelView):
    "Ethnicity"
    _description = __doc__

    _name = "gnuhealth.ethnicity"
    name = fields.Char('Name', required="1", translate=True)
    code = fields.Char('Code')
    notes = fields.Char('Notes')

    def __init__(self):
        super(Ethnicity, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Name must be unique !')]

Ethnicity()


class MedicalSpecialty(ModelSQL, ModelView):
    "Medical Specialty"
    _description = __doc__

    _name = "gnuhealth.specialty"
    name = fields.Char('Specialty', required="1", translate=True,
        help="ie, Addiction Psychiatry")
    code = fields.Char('Code', help="ie, ADP")

    def __init__(self):
        super(MedicalSpecialty, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Specialty must be unique !')]

MedicalSpecialty()


class Physician(ModelSQL, ModelView):
    "Physician"
    _name = "gnuhealth.physician"
    _description = __doc__

    name = fields.Many2One('party.party', 'Physician',
        required="1", domain=[('is_doctor', '=', True)],
        help="Physician's Name, from the partner list")
    institution = fields.Many2One('party.party', 'Institution',
        domain=[('is_institution', '=', True)],
        help="Instituion where she/he works")
    code = fields.Char('ID', help="MD License ID")
    specialty = fields.Many2One('gnuhealth.specialty',
        'Specialty', help="Specialty Code")
    info = fields.Text('Extra info')

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for doctor in self.browse(ids):
            if doctor.name:
                name = doctor.name.name
                if doctor.name.lastname:
                    name = doctor.name.lastname + ', ' + name

            res[doctor.id] = name
        return res

Physician()


class OperationalArea (ModelSQL, ModelView):
    "Operational Area"
    _name = "gnuhealth.operational_area"
    _description = __doc__
    name = fields.Char('Name',
        help="Operational Area of the city or region", required="1")
    operational_sector = fields.One2Many ('gnuhealth.operational_sector','operational_area',
        'Operational Sector',readonly="1")
        
    info = fields.Text('Extra Information')

    def __init__(self):
        super(OperationalArea, self).__init__()

        self._sql_constraints += [('name_uniq', 'unique (name)',
            'The operational area must be unique !')]

OperationalArea()


class OperationalSector(ModelSQL, ModelView):
    "Operational Sector"
    _name = "gnuhealth.operational_sector"
    _description = __doc__

    name = fields.Char('Op. Sector', required="1",
        help="Region included in an operational area")
    operational_area = fields.Many2One('gnuhealth.operational_area',
     'Operational Area')
    info = fields.Text('Extra Information')

    def __init__(self):
        super(OperationalSector, self).__init__()

        self._sql_constraints += [('name_uniq',
            'unique (name, operational_area)',
        'The operational sector must be unique in each operational area!')]

OperationalSector()


class Family(ModelSQL, ModelView):
    "Family"
    _name = "gnuhealth.family"

    name = fields.Char('Family', required="1",
     help="Family code within an operational sector")
    operational_sector = fields.Many2One('gnuhealth.operational_sector',
        'Operational Sector')
    members = fields.One2Many('gnuhealth.family_member', 'name',
        'Family Members')

    info = fields.Text('Extra Information')

    def __init__(self):
        super(Family, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Family Code must be unique !')]

Family()


class FamilyMember(ModelSQL, ModelView):
    "Family Member"
    _name = "gnuhealth.family_member"

    name = fields.Many2One('gnuhealth.family', 'Family', required="1",
     select="1", help="Family code")
    party = fields.Many2One('party.party', 'Party', required="1",
        domain=[('is_person', '=', True)], help="Family code")
    role = fields.Char('Role', help="Father, Mother, sibbling...")

FamilyMember()

# Use the template as in Product category.

class MedicamentCategory(ModelSQL, ModelView):    
    "Medicament Category"
    _name = "gnuhealth.medicament.category"
    _description = __doc__

    name = fields.Char('Name', required=True, translate=True)
    parent = fields.Many2One('gnuhealth.medicament.category','Parent', select=1)
    childs = fields.One2Many('gnuhealth.medicament.category', 'parent',
            string='Children')

    def __init__(self):
        super(MedicamentCategory, self).__init__()
        self._order.insert(0, ('name', 'ASC'))

        self._constraints += [
            ('check_recursion', 'recursive_categories'),
        ]
        self._error_messages.update({
            'recursive_categories': 'You can not create recursive categories!',
        })

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        def _name(category):
            if category.id in res:
                return res[category.id]
            elif category.parent:
                return _name(category.parent) + ' / ' + category.name
            else:
                return category.name
        for category in self.browse(ids):
            res[category.id] = _name(category)
        return res

MedicamentCategory()



class Medicament(ModelSQL, ModelView):

    "Medicament"
    _description = __doc__
    _name = "gnuhealth.medicament"

    name = fields.Many2One('product.product', 'Product',
        domain=[('is_medicament', '=', True)],
        help="Product Name", required=True)
    active_component = fields.Char('Active component', help="Active Component",
        translate=True)
    category = fields.Many2One('gnuhealth.medicament.category', 'Category', select= True)
    therapeutic_action = fields.Char('Therapeutic effect',
        help="Therapeutic action")
    composition = fields.Text('Composition', help="Components")
    indications = fields.Text('Indication', help="Indications")
    dosage = fields.Text('Dosage Instructions',
        help="Dosage / Indications")
    overdosage = fields.Text('Overdosage', help="Overdosage")
    pregnancy_warning = fields.Boolean('Pregnancy Warning',
        help="The drug represents risk to pregnancy or lactancy")
    pregnancy = fields.Text('Pregnancy and Lactancy',
        help="Warnings for Pregnant Women")

    pregnancy_category = fields.Selection([
                        ('A', 'A'),
                        ('B', 'B'),
                        ('C', 'C'),
                        ('D', 'D'),
                        ('X', 'X'),
                        ('N', 'N'),

                        ], 'Pregnancy Category',
                        help='** FDA Pregancy Categories ***\n' \
                        'CATEGORY A :Adequate and well-controlled human studies have' \
                        ' failed to demonstrate a risk to the fetus in the' \
                        ' first trimester of pregnancy (and there is no ' \
                        'evidence of risk in later trimesters).\n\n' \
                        'CATEGORY B : Animal reproduction studies have failed to' \
                        'demonstrate a risk to the fetus and there are no' \
                        ' adequate and well-controlled studies in pregnant women' \
                        ' OR Animal studies have shown an adverse effect, but' \
                        ' adequate and well-controlled studies in pregnant women' \
                        ' have failed to demonstrate a risk to the fetus in any' \
                        ' trimester.\n\n'
                        'CATEGORY C : Animal reproduction studies have shown an adverse' \
                        ' effect on the fetus and there are no adequate and' \
                        ' well-controlled studies in humans, but potential benefits' \
                        ' may warrant use of the drug in pregnant women despite ' \
                        'potential risks. \n\n' \
                        ' CATEGORY D : There is positive evidence of human fetal ' \
                        ' risk based on adverse reaction data from investigational' \
                        ' or marketing experience or studies in humans, but potential' \
                        ' benefits may warrant use of the drug in pregnant women despite' \
                        ' potential risks.\n\n'
                        'CATEGORY X : Studies in animals or humans have demonstrated' \
                        ' fetal abnormalities and/or there is positive evidence of human' \
                        ' fetal risk based on adverse reaction data from investigational' \
                        ' or marketing experience, and the risks involved in use of the' \
                        ' drug in pregnant women clearly outweigh potential benefits.\n\n' \
                        'CATEGORY N : Not yet classified'
                        )
    
    presentation = fields.Text('Presentation', help="Packaging")
    adverse_reaction = fields.Text('Adverse Reactions')
    storage = fields.Text('Storage Conditions')
    notes = fields.Text('Extra Info')

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for medicament in self.browse(ids):
            name = medicament.name.name
            res[medicament.id] = name
        return res

Medicament()


class PathologyCategory(ModelSQL, ModelView):
    "Disease Categories"
    _description = __doc__
    _name = 'gnuhealth.pathology.category'

    name = fields.Char('Category Name', required=True, translate=True)
    parent = fields.Many2One('gnuhealth.pathology.category',
     'Parent Category', select=True)
    childs = fields.One2Many('gnuhealth.pathology.category',
     'parent', 'Children Category')

    def __init__(self):
        super(PathologyCategory, self).__init__()
        self._order.insert(0, ('name', 'ASC'))

        self._constraints += [
            ('check_recursion', 'recursive_categories')]

        self._error_messages.update({
            'recursive_categories':
            'You can not create recursive categories!'})

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}

        def _name(category):
            if category.id in res:
                return res[category.id]
            elif category.parent:
                return _name(category.parent) + ' / ' + category.name
            else:
                return category.name
        for category in self.browse(ids):
            res[category.id] = _name(category)
        return res

PathologyCategory()


class Pathology (ModelSQL, ModelView):
    "Diseases"
    _name = "gnuhealth.pathology"
    name = fields.Char('Name', help="Disease name", required=True, translate=True)
    code = fields.Char('Code',
        help='Specific Code for the Disease (eg, ICD-10, SNOMED...\)')
    category = fields.Many2One('gnuhealth.pathology.category',
        'Disease Category')
    chromosome = fields.Char('Affected Chromosome',
     help="chromosome number")
    protein = fields.Char('Protein involved',
     help="Name of the protein(s) affected")
    gene = fields.Char('Gene', help="Name of the gene(s) affected")
    info = fields.Text('Extra Info')

    def __init__(self):
        super(Pathology, self).__init__()
        self._sql_constraints += [('code_uniq', 'unique (code)',
        'The disease code must be unique')]

Pathology()


class ProcedureCode(ModelSQL, ModelView):
    "Medical Procedures"
    _name = "gnuhealth.procedure"
    _description = __doc__

    name = fields.Char('Code', required=True )
    description = fields.Char('Long Text', translate=True)

ProcedureCode()


class InsurancePlan(ModelSQL, ModelView):
    "Insurance Plan"
    _name = "gnuhealth.insurance.plan"
    _description = __doc__

    name = fields.Many2One('product.product', 'Plan',
     domain=[('type', '=', "service")],
      help="Insurance company plan", required=True)

    company = fields.Many2One('party.party', 'Insurance Company',
     domain=[('is_insurance_company', '=', True)], required=True)

    is_default = fields.Boolean('Default plan',
        help='Check if this is the default plan when assigning ' \
        'this insurance company to a patient')
    notes = fields.Text('Extra info')

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for plan in self.browse(ids):
            if plan.name:
                name = plan.name.name
            res[plan.id] = name
        return res


InsurancePlan()


class Insurance(ModelSQL, ModelView):
    "Insurance"
    _name = "gnuhealth.insurance"
    _description = __doc__

    name = fields.Many2One('party.party', 'Owner')
    number = fields.Char('Number', required=True)
    company = fields.Many2One('party.party', 'Insurance Company',required=True,
     domain=[('is_insurance_company', '=', True)], select=True)

    member_since = fields.Date('Member since')
    member_exp = fields.Date('Expiration date')
    category = fields.Char('Category',
     help="Insurance company plan / category")
    insurance_type = fields.Selection([
                            ('state', 'State'),
                            ('labour_union', 'Labour Union / Syndical'),
                            ('private', 'Private'),
                            ], 'Insurance Type', select=True)

    plan_id = fields.Many2One('gnuhealth.insurance.plan',
     'Plan', help="Insurance company plan")

    notes = fields.Text('Extra Info')

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for insurance in self.browse(ids):
            if insurance.company:
                name = insurance.company.name + ' : ' + insurance.number
            res[insurance.id] = name
        return res

Insurance()


class PartyPatient (ModelSQL, ModelView):
    "Party"
    _name = "party.party"

    activation_date = fields.Date('Activation date',
     help="Date of activation of the party")
    alias = fields.Char('Alias', help="Common name that the Party is reffered")
    ref = fields.Char('SSN', help="Patient Social Security Number or equivalent")
    is_person = fields.Boolean('Person',
     help="Check if the party is a person.")
    is_patient = fields.Boolean('Patient',
     help="Check if the party is a patient")
    is_doctor = fields.Boolean('Doctor',
     help="Check if the party is a doctor")
    is_institution = fields.Boolean('Institution',
     help="Check if the party is a Medical Center")
    is_insurance_company = fields.Boolean('Insurance Company',
     help="Check if the party is an Insurance Company")
    lastname = fields.Char('Last Name', help="Last Name")
    insurance = fields.One2Many('gnuhealth.insurance', 'name', "Insurance")
    internal_user = fields.Many2One('res.user', 'Internal User',
     help='In Medical is the user (doctor, nurse) that logins.' \
     'When the party is a ' \
     'doctor or a health proffesional, it will be the user that maps ' \
     'the doctor\'s party name. It must be present.')
    insurance_company_type = fields.Selection([
                            ('state', 'State'),
                            ('labour_union', 'Labour Union / Syndical'),
                            ('private', 'Private'),
                                ], 'Insurance Type', select=True)
    insurance_plan_ids = fields.One2Many('gnuhealth.insurance.plan',
     'company', "Insurance Plans")

    def __init__(self):
        super(PartyPatient, self).__init__()
        self._sql_constraints += [
            ('ref_uniq', 'UNIQUE(ref)', 'The Patient SSN must be unique')]

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for patient in self.browse(ids):
            name = patient.name
            if patient.lastname:
                name = patient.lastname + ', ' + patient.name
            res[patient.id] = name
        return res


PartyPatient()


class PartyAddress(ModelSQL, ModelView):
    "Party Address"
    _name = "party.address"

    relationship = fields.Char('Relationship',
     help='Include the relationship with the patient ' \
     '- friend, co-worker, brother, ...')
    relative_id = fields.Many2One('party.party',
    'Relative ID', domain=[('is_patient', '=', True)],
     help="If the relative is also a patient, please include it here")

PartyAddress()


class Product(ModelSQL, ModelView):
    "Product"
    _name = "product.product"
    _description = __doc__

    is_medicament = fields.Boolean('Medicament',
     help="Check if the product is a medicament")
    is_vaccine = fields.Boolean('Vaccine',
     help="Check if the product is a vaccine")
    is_bed = fields.Boolean('Bed',
     help="Check if the product is a bed on the gnuhealth.center")

Product()


# GNU HEALTH SEQUENCES

class GnuHealthSequences(ModelSingleton, ModelSQL, ModelView):
    "Standard Sequences for GNU Health"

    _description = __doc__
    _name = "gnuhealth.sequences"

    patient_sequence = fields.Property(fields.Many2One('ir.sequence',
        'Patient Sequence', domain=[('code', '=', 'gnuhealth.patient')],
        required=True))

    appointment_sequence = fields.Property(fields.Many2One('ir.sequence',
        'Appointment Sequence', domain=[('code', '=', 'gnuhealth.appointment')],
        required=True))

    prescription_sequence = fields.Property(fields.Many2One('ir.sequence',
        'Prescription Sequence',
        domain=[('code', '=', 'gnuhealth.prescription.order')],
        required=True))

GnuHealthSequences()


# PATIENT GENERAL INFORMATION
class PatientData(ModelSQL, ModelView):

    "Patient related information"
    _description = __doc__
    _name = "gnuhealth.patient"

# Get the patient age in the following format : "YEARS MONTHS DAYS"
# It will calculate the age of the patient while the patient is alive.
# When the patient dies, it will show the age at time of death.

    def patient_age(self, ids, name):

        def compute_age_from_dates(patient_dob, patient_deceased,
            patient_dod):
            now = datetime.now()
            if (patient_dob):
                dob = datetime.strptime(str(patient_dob), '%Y-%m-%d')

                if patient_deceased:
                    dod = datetime.strptime(patient_dod, '%Y-%m-%d %H:%M:%S')
                    delta = relativedelta(dod, dob)
                    deceased = " (deceased)"
                else:
                    delta = relativedelta(now, dob)
                    deceased = ''
                years_months_days = str(delta.years) + 'y ' + \
                str(delta.months) + "m " + str(delta.days) + \
                "d" + deceased
            else:
                years_months_days = "No DoB !"

            return years_months_days

        result = {}

        for patient_data in self.browse(ids):
            result[patient_data.id] = compute_age_from_dates(patient_data.dob,
            patient_data.deceased, patient_data.dod)
        return result

    name = fields.Many2One('party.party', 'Patient', required="1",
        domain=[('is_patient', '=', True), ('is_person', '=', True)],
        help="Patient Name")
    lastname = fields.Function(fields.Char('Lastname'),
        'get_patient_lastname', searcher="search_patient_lastname")

    ssn = fields.Function(fields.Char('SSN'),
        'get_patient_ssn', searcher="search_patient_ssn")

    identification_code = fields.Char('ID', readonly=True,
       help='Patient Identifier provided by the Health Center.' \
        'Is not the Social Security Number')

    family = fields.Many2One('gnuhealth.family',
        'Family', help="Family Code")
    current_insurance = fields.Many2One('gnuhealth.insurance',
        'Insurance', domain=[('name', '=', Eval('name'))],
        help='Insurance information. You may choose from the' \
        ' different insurances belonging to the patient')
    current_address = fields.Many2One('party.address',
        'Address', domain=[('party', '=', Eval('name'))],
        help='Contact information. You may choose from the' \
        ' different contacts and addresses this patient has.')
    primary_care_doctor = fields.Many2One('gnuhealth.physician',
        'Primary Care Doctor', help="Current primary care / family doctor")
    photo = fields.Binary('Picture')
    dob = fields.Date('DoB', help="Date of Birth")
    age = fields.Function(fields.Char('Age'), 'patient_age')
    sex = fields.Selection([
        ('m', 'Male'),
        ('f', 'Female'),
        ], 'Sex', select=True)
    marital_status = fields.Selection([
        ('s', 'Single'),
        ('m', 'Married'),
        ('w', 'Widowed'),
        ('d', 'Divorced'),
        ('x', 'Separated'),
        ], 'Marital Status', sort=False)
    blood_type = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
        ], 'Blood Type')
    rh = fields.Selection([
        ('+', '+'),
        ('-', '-'),
        ], 'Rh')

    ethnic_group = fields.Many2One('gnuhealth.ethnicity', 'Ethnic group')
    vaccinations = fields.One2Many('gnuhealth.vaccination',
        'name', "Vaccinations")
    medications = fields.One2Many('gnuhealth.patient.medication',
        'name', 'Medications')
    prescriptions = fields.One2Many('gnuhealth.prescription.order',
        'name', "Prescriptions")
    diseases = fields.One2Many('gnuhealth.patient.disease', 'name',
        'Diseases')
    critical_info = fields.Text('Important disease, allergy or' \
        ' procedures information',
        help='Write any important information on the patient\'s disease' \
        ', surgeries, allergies, ...')
# Not used anymore . Now we relate with a shortcut. Clearer
    evaluation_ids = fields.One2Many('gnuhealth.patient.evaluation',
        'patient', 'Evaluation')
    admissions_ids = fields.One2Many('gnuhealth.patient.admission',
        'name', 'Admission / Discharge')
    general_info = fields.Text('General Information',
        help="General information about the patient")
    deceased = fields.Boolean('Deceased',
        help="Mark if the patient has died")
    dod = fields.DateTime('Date of Death',
        states={'invisible': Not(Bool(Eval('deceased'))),
        'required': Bool(Eval('deceased'))})
    cod = fields.Many2One('gnuhealth.pathology', 'Cause of Death',
     states={'invisible': Not(Bool(Eval('deceased'))),
      'required': Bool(Eval('deceased'))})

    def get_patient_ssn(self, ids, name):
        res = {}
        for patient in self.browse(ids):
            res[patient.id] = patient.name.ref
        return res

    def search_patient_ssn(self, name, clause):
        res = []
        value = clause[2]
        res.append(('name.ref', clause[1], value))
        return res


    def get_patient_lastname(self, ids, name):
        res = {}
        for patient in self.browse(ids):
            res[patient.id] = patient.name.lastname
        return res

    def search_patient_lastname(self, name, clause):
        res = []
        value = clause[2]
        res.append(('name.lastname', clause[1], value))
        return res

    def __init__(self):
        super(PatientData, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name)',
            'The Patient already exists !')]

    def create(self, values):
        sequence_obj = Pool().get('ir.sequence')
        config_obj = Pool().get('gnuhealth.sequences')

        values = values.copy()
        if not values.get('identification_code'):
            config = config_obj.browse(1)
            values['identification_code'] = sequence_obj.get_id(
            config.patient_sequence.id)

        return super(PatientData, self).create(values)

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for patient in self.browse(ids):
            if patient.name:
                name = patient.name.name
                if patient.name.lastname:
                    name = patient.name.lastname + ', ' + name
            res[patient.id] = name
        return res


PatientData()

# PATIENT DISESASES INFORMATION


class PatientDiseaseInfo (ModelSQL, ModelView):
    "Patient Disease History"
    _description = __doc__
    _name = "gnuhealth.patient.disease"

    name = fields.Many2One('gnuhealth.patient', 'Patient')
    pathology = fields.Many2One('gnuhealth.pathology', 'Disease',
        required=True, help="Disease")
    disease_severity = fields.Selection([
        ('1_mi', 'Mild'),
        ('2_mo', 'Moderate'),
        ('3_sv', 'Severe'),
        ], 'Severity', select=True, sort=False)
    is_on_treatment = fields.Boolean('Currently on Treatment')
    is_infectious = fields.Boolean('Infectious Disease',
        help="Check if the patient has an infectious / transmissible disease")
    short_comment = fields.Char('Remarks',
        help='Brief, one-line remark of the disease. Longer description ' \
        'will go on the Extra info field')
    doctor = fields.Many2One('gnuhealth.physician', 'Physician',
        help="Physician who treated or diagnosed the patient")
    diagnosed_date = fields.Date('Date of Diagnosis')
    healed_date = fields.Date('Healed')
    is_active = fields.Boolean('Active disease')
    age = fields.Integer('Age when diagnosed',
        help='Patient age at the moment of the diagnosis. Can be estimative')
    pregnancy_warning = fields.Boolean('Pregnancy warning')
    weeks_of_pregnancy = fields.Integer('Contracted in pregnancy week #')
    is_allergy = fields.Boolean('Allergic Disease')
    allergy_type = fields.Selection([
        ('da', 'Drug Allergy'),
        ('fa', 'Food Allergy'),
        ('ma', 'Misc Allergy'),
        ('mc', 'Misc Contraindication'),
        ], 'Allergy type', select=True, sort=False)
    pcs_code = fields.Many2One('gnuhealth.procedure', 'Code',
        help="Procedure code, for example, ICD-10-PCS Code 7-character string")
    treatment_description = fields.Char('Treatment Description')
    date_start_treatment = fields.Date('Start', help="Start of treatment date")
    date_stop_treatment = fields.Date('End', help="End of treatment date")
    status = fields.Selection([
        ('a', 'acute'),
        ('c', 'chronic'),
        ('u', 'unchanged'),
        ('h', 'healed'),
        ('i', 'improving'),
        ('w', 'worsening'),
        ], 'Status of the disease', select=True, sort=False)
    extra_info = fields.Text('Extra Info')

    def default_is_active(self):
        return True

    def __init__(self):
        super(PatientDiseaseInfo, self).__init__()
        self._order.insert(0, ('is_active', 'DESC'))
        self._order.insert(1, ('disease_severity', 'DESC'))
        self._order.insert(2, ('is_infectious', 'DESC'))
        self._order.insert(3, ('diagnosed_date', 'DESC'))

PatientDiseaseInfo()

# PATIENT APPOINTMENT


class Appointment (ModelSQL, ModelView):
    "Patient Appointments"
    _name = "gnuhealth.appointment"
    _description = __doc__

    name = fields.Char('Appointment ID', readonly=True)
    doctor = fields.Many2One('gnuhealth.physician', 'Physician',
        select="1", help="Physician's Name")
    patient = fields.Many2One('gnuhealth.patient', 'Patient', required=True,
        select="1", help="Patient Name")
    appointment_date = fields.DateTime('Date and Time')
    institution = fields.Many2One('party.party', 'Health Center',
        domain=[('is_institution', '=', True)], help="Medical Center")
    speciality = fields.Many2One('gnuhealth.specialty', 'Specialty',
        help="Medical Specialty / Sector")
    urgency = fields.Selection([
            ('a', 'Normal'),
            ('b', 'Urgent'),
            ('c', 'Medical Emergency'),
            ], 'Urgency Level', sort=False)

    comments = fields.Text('Comments')

    appointment_type = fields.Selection([
            ('ambulatory', 'Ambulatory'),
            ('outpatient', 'Outpatient'),
            ('inpatient', 'Inpatient'),
            ], 'Type', sort=False)
    consultations = fields.Many2One('product.product', 'Consultation Services',
        domain=[('type', '=', "service")], help="Consultation Services")

    def __init__(self):
        super(Appointment, self).__init__()
        self._order.insert(0, ('name', 'DESC'))

    def create(self, values):
        sequence_obj = Pool().get('ir.sequence')
        config_obj = Pool().get('gnuhealth.sequences')

        values = values.copy()
        if not values.get('name'):
            config = config_obj.browse(1)
            values['name'] = sequence_obj.get_id(
            config.appointment_sequence.id)

        return super(Appointment, self).create(values)

    def default_urgency(self):
        return 'a'

    def default_appointment_date(self):
        return datetime.now()

    def default_appointment_type(self):
        return 'ambulatory'

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for appointment in self.browse(ids):
            if appointment.name:
                name = appointment.name
#                name = str(appointment['appointment_date'])
            res[appointment.id] = name
        return res
Appointment()


# MEDICATION TEMPLATE
# TEMPLATE USED IN MEDICATION AND PRESCRIPTION ORDERS

class MedicationTemplate(ModelSQL, ModelView):
    "Template for medication"
    _description = __doc__
    _name = "gnuhealth.medication.template"

    medicament = fields.Many2One('gnuhealth.medicament', 'Medicament',
        required=True, help='Prescribed Medicament')
    indication = fields.Many2One('gnuhealth.pathology', 'Indication',
        help='Choose a disease for this medicament from the disease list.' \
        ' It can be an existing disease of the patient or a prophylactic.')
    dose = fields.Float('Dose',
        help="Amount of medication (eg, 250 mg) per dose")
    dose_unit = fields.Many2One('gnuhealth.dose.unit', 'dose unit',
        help='Unit of measure for the medication to be taken')
    route = fields.Many2One('gnuhealth.drug.route', 'Administration Route',
        help="Drug administration route code.")
    form = fields.Many2One('gnuhealth.drug.form', 'Form',
        help="Drug form, such as tablet or gel")
    qty = fields.Integer('x',
        help="Quantity of units (eg, 2 capsules) of the medicament")
    common_dosage = fields.Many2One('gnuhealth.medication.dosage', 'Frequency',
        help="Common / standard dosage frequency for this medicament")
    frequency = fields.Integer('Frequency',
        help='Time in between doses the patient must wait (ie, for 1 pill' \
        ' each 8 hours, put here 8 and select \"hours\" in the unit field')
    frequency_unit = fields.Selection([
        ('seconds', 'seconds'),
        ('minutes', 'minutes'),
        ('hours', 'hours'),
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('wr', 'when required')
        ], 'unit', select=True, sort=False)
    admin_times = fields.Char('Admin hours',
        help='Suggested administration hours. For example, at 08:00, ' \
        '13:00 and 18:00 can be encoded like 08 13 18')
    duration = fields.Integer('Treatment duration',
        help='Period that the patient must take the medication. in ' \
        'minutes, hours, days, months, years or indefinately')
    duration_period = fields.Selection([
            ('minutes', 'minutes'),
            ('hours', 'hours'),
            ('days', 'days'),
            ('months', 'months'),
            ('years', 'years'),
            ('indefinite', 'indefinite')], 'Treatment period',
            help='Period that the patient must take the medication in ' \
            'minutes, hours, days, months, years or indefinately', sort=False)
    start_treatment = fields.DateTime('Start', help="Date of start of Treatment")
    end_treatment = fields.DateTime('End', help="Date of start of Treatment")

MedicationTemplate()


# PATIENT MEDICATION TREATMENT
class PatientMedication(ModelSQL, ModelView):
    "Patient Medication"
    _description = __doc__
    _name = "gnuhealth.patient.medication"
    _inherits = {"gnuhealth.medication.template": "template"}

    template = fields.Many2One('gnuhealth.medication.template',
        'Medication Template')
    name = fields.Many2One('gnuhealth.patient', 'Patient', readonly=True)
    doctor = fields.Many2One('gnuhealth.physician', 'Physician',
        help="Physician who prescribed the medicament")
    is_active = fields.Boolean('Active',
        help="Check if the patient is currently taking the medication",
        on_change_with=['discontinued', 'course_completed'])
    discontinued = fields.Boolean('Discontinued',
        on_change_with=['is_active', 'course_completed'])
    course_completed = fields.Boolean('Course Completed',
        on_change_with=['is_active', 'discontinued'])
    discontinued_reason = fields.Char('Reason for discontinuation',
        help="Short description for discontinuing the treatment",
         states={'invisible': Not(Bool(Eval('discontinued'))),
         'required': Bool(Eval('discontinued'))})
    adverse_reaction = fields.Text('Adverse Reactions',
        help="Side effects or adverse reactions that the patient experienced")
    notes = fields.Text('Extra Info')
    patient = fields.Many2One('gnuhealth.patient', 'Patient')

    def on_change_with_is_active (self, vals):
        discontinued = vals.get('discontinued')
        course_completed = vals.get('course_completed')
        is_active = True
        if (discontinued or course_completed):
            is_active = False
        return is_active

    def on_change_with_discontinued (self, vals):
        discontinued = vals.get('discontinued')
        is_active = vals.get('is_active')
        course_completed = vals.get('course_completed')

        if (is_active or course_completed):
                discontinued = False
        return ( discontinued ) 
        
    def on_change_with_course_completed (self, vals):
        is_active = vals.get('is_active')
        course_completed = vals.get('discontinued')
        discontinued = vals.get('discontinued')

        if (is_active or discontinued):
                course_completed = False
        return ( course_completed ) 

    def default_is_active(self):
        return True

#    def default_start_treatment(self):
#        return time.strftime('%Y-%m-%d %H:%M:%S')

    def default_frequency_unit(self):
        return 'hours'

    def default_duration_period(self):
        return 'days'

    def default_qty(self):
        return 1


PatientMedication()


# PATIENT VACCINATION INFORMATION

class PatientVaccination(ModelSQL, ModelView):
    "Patient Vaccination information"
    _description = __doc__
    _name = "gnuhealth.vaccination"

    def check_vaccine_expiration_date(self, ids):

        vaccine = self.browse(ids[0])
        if vaccine.vaccine_expiration_date:
            if vaccine.vaccine_expiration_date < datetime.date(vaccine.date):
                return False
        return True

    name = fields.Many2One('gnuhealth.patient', 'Patient', readonly=True)
    vaccine = fields.Many2One('product.product', 'Name',
        domain=[('is_vaccine', '=', True)], required="1",
        help='Vaccine Name. Make sure that the vaccine (product) has' \
        ' all the proper information at product level. Information such' \
        ' as provider, supplier code, tracking number, etc.. This ' \
        ' information must always be present. If available, please copy' \
        ' / scan the vaccine leaflet and attach it to this record')
    vaccine_expiration_date = fields.Date('Expiration date')
    vaccine_lot = fields.Char('Lot Number',
    help='Please check on the vaccine (product) production lot number'\
     'and tracking number when available !')
    institution = fields.Many2One('party.party', 'Institution',
        domain=[('is_institution', '=', True)],
        help="Medical Center where the patient is being or was vaccinated")
    date = fields.DateTime('Date')
    dose = fields.Integer('Dose Number')
    next_dose_date = fields.DateTime('Next Dose')
    observations = fields.Char('Observations')

    def __init__(self):
        super(PatientVaccination, self).__init__()

        self._sql_constraints = [
            ('dose_uniq', 'UNIQUE(name,vaccine,dose)',
            'This vaccine dose has been given already to the patient')]

        self._constraints = [
            ('check_vaccine_expiration_date', 'expired_vaccine')]
        self._error_messages.update({
            'expired_vaccine': 'EXPIRED VACCINE. PLEASE INFORM' \
            ' THE LOCAL HEALTH AUTHORITIES AND DO NOT USE IT !!!',
        })

    def default_date(self):
        return datetime.now()

    def default_dose(self):
        return 1


PatientVaccination()


class PatientPrescriptionOrder(ModelSQL, ModelView):
    "Prescription Order"
    _name = "gnuhealth.prescription.order"
    _description = __doc__

    patient = fields.Many2One('gnuhealth.patient', 'Patient', required=True,
     select="1")
    prescription_id = fields.Char('Prescription ID',
        readonly=True, help='Type in the ID of this prescription')
    prescription_date = fields.DateTime('Prescription Date')
    user_id = fields.Many2One('res.user', 'Prescribing Doctor', readonly=True,
     select="1")
    pharmacy = fields.Many2One('party.party', 'Pharmacy')
    prescription_line = fields.One2Many('gnuhealth.prescription.line',
        'name', 'Prescription line')
    notes = fields.Text('Prescription Notes')

    def default_prescription_date(self):
        return datetime.now()

    def default_user_id(self):
        user_obj = Pool().get('res.user')
        user = user_obj.browse(Transaction().user)
        return int(user.id)

    def create(self, values):
        sequence_obj = Pool().get('ir.sequence')
        config_obj = Pool().get('gnuhealth.sequences')

        values = values.copy()
        if not values.get('prescription_id'):
            config = config_obj.browse(1)
            values['prescription_id'] = sequence_obj.get_id(
            config.prescription_sequence.id)

        return super(PatientPrescriptionOrder, self).create(values)

PatientPrescriptionOrder()


# PRESCRIPTION LINE
class PrescriptionLine(ModelSQL, ModelView):
    "Prescription Line"
    _name = "gnuhealth.prescription.line"
    _description = __doc__
    _inherits = {"gnuhealth.medication.template": "template"}

    template = fields.Many2One('gnuhealth.medication.template',
        'Medication Template')
    name = fields.Many2One('gnuhealth.prescription.order', 'Prescription ID')
    review = fields.DateTime('Review')
    quantity = fields.Integer('Quantity')
    refills = fields.Integer('Refills #')
    allow_substitution = fields.Boolean('Allow substitution')
    short_comment = fields.Char('Comment',
        help='Short comment on the specific drug')
    prnt = fields.Boolean('Print',
        help='Check this box to print this line of the prescription.')

    def default_qty(self):
        return 1

    def default_duration_period(self):
        return 'days'

    def default_frequency_unit(self):
        return 'hours'

    def default_quantity(self):
        return 1

    def default_prnt(self):
        return True

PrescriptionLine()


# PATIENT DIRECTIONS
class Directions(ModelSQL, ModelView):
    "Patient Directions"
    _name = "gnuhealth.directions"
    _description = __doc__
    name = fields.Many2One('gnuhealth.patient', 'Patient', readonly=True)
    procedure = fields.Many2One('gnuhealth.procedure', 'Procedure')
    comments = fields.Char('Comments')

Directions()


class PatientEvaluation(ModelSQL, ModelView):
    "Patient Evaluation"
    _name = "gnuhealth.patient.evaluation"
    _description = __doc__

    patient = fields.Many2One('gnuhealth.patient', 'Patient')
    evaluation_date = fields.Many2One('gnuhealth.appointment', 'Appointment', 
        help='Enter or select the date / ID of the appointment' \
        ' related to this evaluation')
    evaluation_start = fields.DateTime('Start of Evaluation',
     required=True)
    evaluation_endtime = fields.DateTime('End of Evaluation', required="1")
    next_evaluation = fields.Many2One('gnuhealth.appointment',
        'Next Appointment')
    user_id = fields.Many2One('res.user', 'Last Changed by', readonly=True)
    derived_from = fields.Many2One('gnuhealth.physician', 'Derived from Doctor',
        help="Physician who escalated / derived the case")
    derived_to = fields.Many2One('gnuhealth.physician', 'Derived to Doctor',
        help="Physician to whom escalate / derive the case")
    evaluation_type = fields.Selection([
       ('a', 'Ambulatory'),
       ('e', 'Emergency'),
       ('i', 'Inpatient'),
       ('pa', 'Pre-arraganged appointment'),
       ('pc', 'Periodic control'),
       ('p', 'Phone call'),
       ('t', 'Telemedicine'),
        ], 'Evaluation Type', sort=False)
    chief_complaint = fields.Char('Chief Complaint', help='Chief Complaint')
    notes_complaint = fields.Text('Complaint details')
    evaluation_summary = fields.Text('Evaluation Summary')
    glycemia = fields.Float('Glycemia',
        help="Last blood glucose level. Can be approximative.")
    hba1c = fields.Float('Glycated Hemoglobin',
        help="Last Glycated Hb level. Can be approximative.")
    cholesterol_total = fields.Integer('Last Cholesterol',
        help="Last cholesterol reading. Can be approximative")
    hdl = fields.Integer('Last HDL',
        help="Last HDL Cholesterol reading. Can be approximative")
    ldl = fields.Integer('Last LDL',
        help="Last LDL Cholesterol reading. Can be approximative")
    tag = fields.Integer('Last TAGs',
        help="Triacylglycerol(triglicerides) level. Can be approximative")
    systolic = fields.Integer('Systolic Pressure')
    diastolic = fields.Integer('Diastolic Pressure')
    bpm = fields.Integer('Heart Rate',
        help="Heart rate expressed in beats per minute")
    respiratory_rate = fields.Integer('Respiratory Rate',
        help="Respiratory rate expressed in breaths per minute")
    osat = fields.Integer('Oxygen Saturation',
        help="Oxygen Saturation(arterial).")
    malnutrition = fields.Boolean('Malnutrition',
        help='Check this box if the patient show signs of malnutrition.' \
        ' If associated  to a disease, please encode the' \
        ' correspondent disease on the patient disease history. For' \
        ' example, Moderate protein-energy malnutrition,' \
        ' E44.0 in ICD-10 encoding')
    dehydration = fields.Boolean('Dehydration',
        help='Check this box if the patient show signs of dehydration.' \
        ' If associated  to a disease, please encode the ' \
        ' correspondent disease on the patient disease history. For ' \
        'example, Volume Depletion, E86 in ICD-10 encoding')
    temperature = fields.Float('Temperature',
        help="Temperature in celcius")
    weight = fields.Float('Weight', help="Weight in Kilos")
    height = fields.Float('Height', help="Height in centimeters, eg 175")
    bmi = fields.Float('Body Mass Index',
        on_change_with=['weight', 'height', 'bmi'])
    head_circumference = fields.Float('Head Circumference',
        help="Head circumference")
    abdominal_circ = fields.Float('Abdominal Circumference')
    edema = fields.Boolean('Edema', help='Please also encode the ' \
        'correspondent disease on the patient disease history.' \
        ' For example,  R60.1 in ICD-10 encoding')
    petechiae = fields.Boolean('Petechiae')
    hematoma = fields.Boolean('Hematomas')
    cyanosis = fields.Boolean('Cyanosis', help='If associated  to a' \
     ' disease, please encode it on the patient disease history.' \
     ' For example,  R23.0 in ICD-10 encoding')
    acropachy = fields.Boolean('Acropachy',
        help='Check if the patient shows acropachy / clubbing')
    nystagmus = fields.Boolean('Nystagmus',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history. For example,  H55 in ICD-10 encoding')
    miosis = fields.Boolean('Miosis', help='If associated  to a' \
    ' disease, please encode it on the patient disease history.' \
    ' For example,  H57.0 in ICD-10 encoding')
    mydriasis = fields.Boolean('Mydriasis',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history. For example,  H57.0 in ICD-10 encoding')
    cough = fields.Boolean('Cough',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history.')
    palpebral_ptosis = fields.Boolean('Palpebral Ptosis',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history')
    arritmia = fields.Boolean('Arritmias',
        help='If associated  to a disease, please encode it on the' \
        'patient disease history')
    heart_murmurs = fields.Boolean('Heart Murmurs')
    heart_extra_sounds = fields.Boolean('Heart Extra Sounds',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history')
    jugular_engorgement = fields.Boolean('Jugular Engorgement',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history')
    ascites = fields.Boolean('Ascites',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history')
    lung_adventitious_sounds = fields.Boolean('Lung Adventitious sounds',
        help="Crackles, wheezes, ronchus..")
    bronchophony = fields.Boolean('Bronchophony')
    increased_fremitus = fields.Boolean('Increased Fremitus')
    decreased_fremitus = fields.Boolean('Decreased Fremitus')
    jaundice = fields.Boolean('Jaundice',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history')
    lynphadenitis = fields.Boolean('Linphadenitis',
        help='If associated  to a disease, please encode it on the' \
        ' patient disease history')
    breast_lump = fields.Boolean('Breast Lumps')
    breast_asymmetry = fields.Boolean('Breast Asymmetry')
    nipple_inversion = fields.Boolean('Nipple Inversion')
    nipple_discharge = fields.Boolean('Nipple Discharge')
    peau_dorange = fields.Boolean('Peau d orange',
        help='Check if the patient has prominent pores in the skin ' \
        'of the breast')
    gynecomastia = fields.Boolean('Gynecomastia')

    masses = fields.Boolean('Masses', help='Check when there are' \
        ' findings of masses / tumors / lumps')
    hypotonia = fields.Boolean('Hypotonia', help='Please also encode ' \
        'the correspondent disease on the patient disease history.')
    hypertonia = fields.Boolean('Hypertonia',
        help='Please also encode the correspondent disease on the' \
        ' patient disease history.')
    pressure_ulcers = fields.Boolean('Pressure Ulcers',
        help='Check when Decubitus / Pressure ulcers are present')
    goiter = fields.Boolean('Goiter')
    alopecia = fields.Boolean('Alopecia',
        help='Check when alopecia - including androgenic - is present')
    xerosis = fields.Boolean('Xerosis')
    erithema = fields.Boolean('Erithema',
        help='Please also encode the correspondent disease' \
        ' on the patient disease history.')
    loc = fields.Integer('Level of Consciousness',
        help='Level of Consciousness - on Glasgow Coma Scale :' \
        '  1=coma - 15=normal',
        on_change_with=['loc_verbal', 'loc_motor', 'loc_eyes'])
    loc_eyes = fields.Selection([
       ('1', 'Does not Open Eyes'),
       ('2', 'Opens eyes in response to painful stimuli'),
       ('3', 'Opens eyes in response to voice'),
       ('4', 'Opens eyes spontaneously'),
        ], 'Glasgow - Eyes', sort=False)

    loc_verbal = fields.Selection([
       ('1', 'Makes no sounds'),
       ('2', 'Incomprehensible sounds'),
       ('3', 'Utters inappropriate words'),
       ('4', 'Confused, disoriented'),
       ('5', 'Oriented, converses normally'),
        ], 'Glasgow - Verbal', sort=False)

    loc_motor = fields.Selection([
       ('1', 'Makes no movement'),
       ('2', 'Extension to painful stimuli - decerebrate response -'),
       ('3', 'Abnormal flexion to painful stimuli (decorticate response)'),
       ('4', 'Flexion / Withdrawal to painful stimuli'),
       ('5', 'Localizes painful stimuli'),
       ('6', 'Obeys commands'),
        ], 'Glasgow - Motor', sort=False)

    tremor = fields.Boolean('Tremor', help='If associated  to a ' \
        'disease, please encode it on the patient disease history')
    violent = fields.Boolean('Violent Behaviour',
        help='Check this box if the patient is agressive or violent at ' \
        'the moment')
    mood = fields.Selection([
                           ('n', 'Normal'),
                           ('s', 'Sad'),
                           ('f', 'Fear'),
                           ('r', 'Rage'),
                           ('h', 'Happy'),
                           ('d', 'Disgust'),
                           ('e', 'Euphoria'),
                           ('fl', 'Flat'),
                            ], 'Mood', sort=False)

    orientation = fields.Boolean('Orientation', help='Check this box if' \
        ' the patient is disoriented in time and/or space')
    memory = fields.Boolean('Memory', help='Check this box if the ' \
        'patient has problems in short or long term memory')
    knowledge_current_events = fields.Boolean('Knowledge of Current' \
        ' Events', help='Check this box if the patient can not respond to '
    'public notorious events')
    judgment = fields.Boolean('Jugdment',
        help='Check this box if the patient can not interpret' \
        ' basic scenario solutions')
    abstraction = fields.Boolean('Abstraction',
        help='Check this box if the patient presents abnormalities in' \
        ' abstract reasoning')
    vocabulary = fields.Boolean('Vocabulary',
        help='Check this box if the patient lacks basic intelectual ' \
        'capacity, when she/he can not describe elementary objects')
    calculation_ability = fields.Boolean('Calculation Ability',
        help='Check this box if the patient can not do simple' \
        ' arithmetic problems')
    object_recognition = fields.Boolean('Object Recognition',
        help='Check this box if the patient suffers from any sort of' \
        ' gnosia disorders, such as agnosia, prosopagnosia ...')
    praxis = fields.Boolean('Praxis',
        help='Check this box if the patient is unable to make voluntary' \
        'movements')
    diagnosis = fields.Many2One('gnuhealth.pathology',
        'Presumptive Diagnosis', help="Presumptive Diagnosis")
    info_diagnosis = fields.Text('Presumptive Diagnosis: Extra Info')
    directions = fields.Text('Plan')
    actions = fields.One2Many('gnuhealth.directions', 'name', 'Procedures', help="Procedures / Actions to take")
    symptom_pain = fields.Boolean('Pain')
    symptom_pain_intensity = fields.Integer('Pain intensity',
        help="Pain intensity from 0(no pain) to 10(worst possible pain)")
    symptom_arthralgia = fields.Boolean('Arthralgia')
    symptom_myalgia = fields.Boolean('Myalgia')
    symptom_abdominal_pain = fields.Boolean('Abdominal Pain')
    symptom_cervical_pain = fields.Boolean('Cervical Pain')
    symptom_thoracic_pain = fields.Boolean('Thoracic Pain')
    symptom_lumbar_pain = fields.Boolean('Lumbar Pain')
    symptom_pelvic_pain = fields.Boolean('Pelvic Pain')
    symptom_headache = fields.Boolean('Headache')
    symptom_odynophagia = fields.Boolean('Odynophagia')
    symptom_sore_throat = fields.Boolean('Sore throat')
    symptom_otalgia = fields.Boolean('Otalgia')
    symptom_tinnitus = fields.Boolean('Tinnitus')
    symptom_ear_discharge = fields.Boolean('Ear Discharge')
    symptom_hoarseness = fields.Boolean('Hoarseness')
    symptom_chest_pain = fields.Boolean('Chest Pain')
    symptom_chest_pain_excercise = fields.Boolean('Chest Pain' \
        'on excercise only')
    symptom_orthostatic_hypotension = fields.Boolean('Orthostatic hypotension',
        help='If associated  to a disease,please encode it on the' \
        ' patient disease history. For example,  I95.1 in ICD-10 encoding')
    symptom_astenia = fields.Boolean('Astenia')
    symptom_anorexia = fields.Boolean('Anorexia')
    symptom_weight_change = fields.Boolean('Sudden weight change')
    symptom_abdominal_distension = fields.Boolean('Abdominal Distension')
    symptom_hemoptysis = fields.Boolean('Hemoptysis')
    symptom_hematemesis = fields.Boolean('Hematemesis')
    symptom_epistaxis = fields.Boolean('Epistaxis')
    symptom_gingival_bleeding = fields.Boolean('Gingival Bleeding')
    symptom_rinorrhea = fields.Boolean('Rinorrhea')
    symptom_nausea = fields.Boolean('Nausea')
    symptom_vomiting = fields.Boolean('Vomiting')
    symptom_dysphagia = fields.Boolean('Dysphagia')
    symptom_polydipsia = fields.Boolean('Polydipsia')
    symptom_polyphagia = fields.Boolean('Polyphagia')
    symptom_polyuria = fields.Boolean('Polyuria')
    symptom_nocturia = fields.Boolean('Nocturia')
    symptom_vesical_tenesmus = fields.Boolean('Vesical Tenesmus')
    symptom_pollakiuria = fields.Boolean('Pollakiuiria')
    symptom_dysuria = fields.Boolean('Dysuria')
    symptom_stress = fields.Boolean('Stressed-out')
    symptom_mood_swings = fields.Boolean('Mood Swings')
    symptom_pruritus = fields.Boolean('Pruritus')
    symptom_insomnia = fields.Boolean('Insomnia')
    symptom_disturb_sleep = fields.Boolean('Disturbed Sleep')
    symptom_dyspnea = fields.Boolean('Dyspnea')
    symptom_orthopnea = fields.Boolean('Orthopnea')
    symptom_amnesia = fields.Boolean('Amnesia')
    symptom_paresthesia = fields.Boolean('Paresthesia')
    symptom_paralysis = fields.Boolean('Paralysis')
    symptom_syncope = fields.Boolean('Syncope')
    symptom_dizziness = fields.Boolean('Dizziness')
    symptom_vertigo = fields.Boolean('Vertigo')
    symptom_eye_glasses = fields.Boolean('Eye glasses',
        help="Eye glasses or contact lenses")
    symptom_blurry_vision = fields.Boolean('Blurry vision')
    symptom_diplopia = fields.Boolean('Diplopia')
    symptom_photophobia = fields.Boolean('Photophobia')
    symptom_dysmenorrhea = fields.Boolean('Dysmenorrhea')
    symptom_amenorrhea = fields.Boolean('Amenorrhea')
    symptom_metrorrhagia = fields.Boolean('Metrorrhagia')
    symptom_menorrhagia = fields.Boolean('Menorrhagia')
    symptom_vaginal_discharge = fields.Boolean('Vaginal Discharge')
    symptom_urethral_discharge = fields.Boolean('Urethral Discharge')
    symptom_diarrhea = fields.Boolean('Diarrhea')
    symptom_constipation = fields.Boolean('Constipation')
    symptom_rectal_tenesmus = fields.Boolean('Rectal Tenesmus')
    symptom_melena = fields.Boolean('Melena')
    symptom_proctorrhagia = fields.Boolean('Proctorrhagia')
    symptom_xerostomia = fields.Boolean('Xerostomia')
    symptom_sexual_dysfunction = fields.Boolean('Sexual Dysfunction')
    notes = fields.Text('Notes')

    def default_loc_eyes(self):
        return 4

    def default_loc_verbal(self):
        return 5

    def default_loc_motor(self):
        return 6

    def default_evaluation_type(self):
        return 'pa'

    def on_change_with_bmi(self, vals):
        height = vals.get('height')
        weight = vals.get('weight')
        if (height > 0):
            bmi = weight / ((height / 100) ** 2)
        else:
            bmi = 0
        return bmi

    def on_change_with_loc(self, vals):
        loc_motor = vals.get('loc_motor')
        loc_eyes = vals.get('loc_eyes')
        loc_verbal = vals.get('loc_verbal')
        loc = int(loc_motor) + int(loc_eyes) + int(loc_verbal)

        return loc

PatientEvaluation()


# HEALTH CENTER / HOSPITAL INFRASTRUCTURE
class HospitalBuilding(ModelSQL, ModelView):
    "Hospital Building"
    _description = __doc__
    _name = "gnuhealth.hospital.building"
    name = fields.Char('Name', required=True,
        help="Name of the building within the institution")
    institution = fields.Many2One('party.party', 'Institution',
        domain=[('is_institution', '=', "1")],
        help="Medical Center")
    code = fields.Char('Code')
    extra_info = fields.Text('Extra Info')

HospitalBuilding()


class HospitalUnit(ModelSQL, ModelView):
    "Hospital Unit"
    _description = __doc__
    _name = "gnuhealth.hospital.unit"
    name = fields.Char('Name', required=True,
        help="Name of the unit, eg Neonatal, Intensive Care, ...")
    institution = fields.Many2One('party.party', 'Institution',
        domain=[('is_institution', '=', "1")],
        help="Medical Center")
    code = fields.Char('Code')
    extra_info = fields.Text('Extra Info')

HospitalUnit()


class HospitalOR(ModelSQL, ModelView):
    "Operating Room"
    _description = __doc__
    _name = "gnuhealth.hospital.or"

    name = fields.Char('Name', required=True,
        help="Name of the Operating Room")
    institution = fields.Many2One('party.party', 'Institution',
        domain=[('is_institution', '=', "1")], help="Medical Center")
    building = fields.Many2One('gnuhealth.hospital.building', 'Building',
        select="1")
    unit = fields.Many2One('gnuhealth.hospital.unit', 'Unit')
    extra_info = fields.Text('Extra Info')

    def __init__(self):
        super(HospitalOR, self).__init__()

        self._sql_constraints = [('name_uniq', 'unique (name, institution)',
            'The Operating Room code must be unique per Health Center')]

HospitalOR()


class HospitalWard(ModelSQL, ModelView):
    "Hospital Ward"
    _name = "gnuhealth.hospital.ward"
    _description = __doc__

    name = fields.Char('Name', required=True,
     help="Ward / Room code")
    institution = fields.Many2One('party.party', 'Institution',
        domain=[('is_institution', '=', "1")], help="Medical Center")
    building = fields.Many2One('gnuhealth.hospital.building', 'Building')
    floor = fields.Integer('Floor Number')
    unit = fields.Many2One('gnuhealth.hospital.unit', 'Unit')
    private = fields.Boolean('Private',
        help="Check this option for private room")
    bio_hazard = fields.Boolean('Bio Hazard',
        help="Check this option if there is biological hazard")
    number_of_beds = fields.Integer('Number of beds',
        help="Number of patients per ward")
    telephone = fields.Boolean('Telephone access')
    ac = fields.Boolean('Air Conditioning')
    private_bathroom = fields.Boolean('Private Bathroom')
    guest_sofa = fields.Boolean('Guest sofa-bed')
    tv = fields.Boolean('Television')
    internet = fields.Boolean('Internet Access')
    refrigerator = fields.Boolean('Refrigetator')
    microwave = fields.Boolean('Microwave')
    gender = fields.Selection((('men', 'Men Ward'), ('women', 'Women Ward'),
        ('unisex', 'Unisex')), 'Gender', required=True, sort=False)
    state = fields.Selection((('beds_available', 'Beds available'),
        ('full', 'Full'), ('na', 'Not available')), 'Status', sort=False)
    extra_info = fields.Text('Extra Info')

    def default_gender(self):
        return 'unisex'

    def default_number_of_beds(self):
        return 1

HospitalWard()


class HospitalBed(ModelSQL, ModelView):
    "Hospital Bed"
    _description = __doc__
    _name = "gnuhealth.hospital.bed"
    name = fields.Many2One('product.product', 'Bed', domain=[('is_bed', '=', True)],
     required=True,  help="Bed Number")
    ward = fields.Many2One('gnuhealth.hospital.ward',
        'Ward', help="Ward or room")
    bed_type = fields.Selection((('gatch', 'Gatch Bed'),
        ('electric', 'Electric'), ('stretcher', 'Stretcher'),
        ('low', 'Low Bed'), ('low_air_loss', 'Low Air Loss'),
        ('circo_electric', 'Circo Electric'),
        ('clinitron', 'Clinitron')), 'Bed Type', required=True, sort=False)
    telephone_number = fields.Char('Telephone Number',
        help="Telephone number / Extension")
    extra_info = fields.Text('Extra Info')
    state = fields.Selection((('free', 'Free'), ('reserved', 'Reserved'),
     ('occupied', 'Occupied'), ('na', 'Not available')), 'Status', sort=False)

    def default_bed_type(self):
        return 'gatch'

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for bed in self.browse(ids):
            if bed.name:
                name = bed.name.name
            res[bed.id] = name
        return res

HospitalBed()
