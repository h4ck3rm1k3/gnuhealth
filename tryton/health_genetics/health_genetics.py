# coding=utf-8

#    Copyright (C) 2008-2011 Luis Falcon

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

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields
from trytond.tools import safe_eval, datetime_strftime
from trytond.transaction import Transaction
from trytond.pyson import Eval


class DiseaseGene(ModelSQL, ModelView):
    'Disease Genes'
    _name = 'gnuhealth.disease.gene'
    _description = __doc__

    name = fields.Char('Official Symbol', select='1')
    long_name = fields.Char('Official Long Name', select='1')
    gene_id = fields.Char('Gene ID',
        help="default code from NCBI Entrez database.", select='2')
    chromosome = fields.Char('Affected Chromosome',
        help="Name of the affected chromosome", select='2')
    location = fields.Char('Location', help="Locus of the chromosome")
    dominance = fields.Selection([
        ('d', 'dominant'),
        ('r', 'recessive'),
        ], 'Dominance', select='2')
    info = fields.Text('Information', help="Name of the protein(s) affected")

    def get_rec_name(self, ids, name):
        if not ids:
            return {}
        res = {}
        for gene in self.browse(ids):
            name = str(gene['name'] + ':' + gene['long_name'])
            res[gene.id] = name
        return res

DiseaseGene()


class PatientGeneticRisk(ModelSQL, ModelView):
    'Patient Genetic Risks'
    _name = 'gnuhealth.patient.genetic.risk'
    _description = __doc__

    patient = fields.Many2One('gnuhealth.patient', 'Patient', select='1')
    disease_gene = fields.Many2One('gnuhealth.disease.gene',
        'Disease Gene', select='1')

PatientGeneticRisk()


class FamilyDiseases(ModelSQL, ModelView):
    'Family Diseases'
    _name = 'gnuhealth.patient.family.diseases'
    _description = __doc__

    patient = fields.Many2One('gnuhealth.patient', 'Patient', select='1')
    name = fields.Many2One('gnuhealth.pathology', 'Disease', select='1')
    xory = fields.Selection([
        ('m', 'Maternal'),
        ('f', 'Paternal'),
        ], 'Maternal or Paternal', select='1')

    relative = fields.Selection([
        ('mother', 'Mother'),
        ('father', 'Father'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('aunt', 'Aunt'),
        ('uncle', 'Uncle'),
        ('nephew', 'Nephew'),
        ('niece', 'Niece'),
        ('grandfather', 'Grandfather'),
        ('grandmother', 'Grandmother'),
        ('cousin', 'Cousin'),
        ], 'Relative',
        help="First degree = siblings, mother and father; second degree = " \
        "Uncles, nephews and Nieces; third degree = Grandparents and cousins",
        select='1')

FamilyDiseases()


class GnuHealthPatient (ModelSQL, ModelView):
    'Add to the Medical patient_data class (gnuhealth.patient) the genetic ' \
    'and family risks'
    _name = 'gnuhealth.patient'
    _description = __doc__

    genetic_risks = fields.One2Many('gnuhealth.patient.genetic.risk',
        'patient', 'Genetic Risks')
    family_history = fields.One2Many('gnuhealth.patient.family.diseases',
        'patient', 'Family History')

GnuHealthPatient()
