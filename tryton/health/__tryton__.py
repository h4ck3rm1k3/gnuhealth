# -*- encoding: utf-8 -*-
{

	'name' : 'GNU Health : Free Health and Hospital Information System',  
    'version': '1.4.1',
	'author' : 'GNU Solidario',
	'email' : 'health@gnusolidario.org',
	'website' : "http://health.gnu.org",
    'depends' : ['ir', 'res', 'product', 'party', 'company'],
    'name_es_ES': 'GNU Health : Sistema Libre de Gestión Hospitalaria y de Salud',
    'translation': [
        'locale/es_ES.po',
    ],

	"xml" : ["health_view.xml","data/medicament_categories.xml",
        "data/WHO_products.xml","data/WHO_list_of_essential_medicines.xml",
        "data/health_specialties.xml","data/ethnic_groups.xml",
        "data/occupations.xml","data/dose_units.xml",
        "data/drug_administration_routes.xml","data/medicament_form.xml",
        "data/medication_frequencies.xml","data/health_sequences.xml",
        "health_report.xml"],

# Use the following lines for Spanish and comment the prior English language ones

#    "xml" : ["health_view.xml","health_report.xml",
#        "data/health_sequences.xml","data/ethnic_groups_es.xml",
#        "data/occupations_es.xml","data/dose_units_es.xml",
#        "data/drug_administration_routes.xml","data/medicament_form_es.xml",
#        "data/medication_frequencies_es.xml","data/medicament_categories.xml",
#        "data/WHO_list_of_essential_medicines.xml",
#        "data/WHO_medicaments.xml","data/health_specialties_es.xml"],

	'description' : """

About GNU Health
----------------------

GNU Health ("Medical") is a multi-user, highly scalable, centralized Health and Hospital Information System.

It provides a free universal Health and Hospital Information System, so doctors and institutions all over the world, specially in developing countries will benefit from a centralized, high quality, secure and scalable system.


GNU Health at a glance:


    * Strong focus in family medicine and Primary Health Care

    * Major interest in Socio-economics (housing conditions, substance abuse, education...)

    * Diseases and Medical procedures standards (like ICD-10 / ICD-10-PCS ...)

    * Patient Genetic and Hereditary risks : Over 4200 genes related to diseases (NCBI / Genecards)

    * Epidemiological and other statistical reports

    * 100% paperless patient examination and history taking

    * Patient Administration (creation, evaluations / consultations, history ... )

    * Doctor Administration

    * Lab Administration

    * Medicine / Drugs information (vademécum)

    * Medical stock and supply chain management

    * Hospital Financial Administration

    * Designed with industry standards in mind

    * Free Software : License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>



Please check the main project at the GNU Savannah (http://savannah.gnu.org/projects/health ) for the latest news and developer releases. 

""",

    'description_es_ES': '''
Acerca de GNU Health
---------------------------------

GNU Health es un sistema libre de Gestión Hospitalaria y de Información de salud que ofrece las siguientes funciones : 

    * Expediente Médico Electrónico (EMR)

    * Sistema de Gestión Hospitalaria (HIS)

    * Sistema de Información de Salud

Nuestro objetivo es contribuir con los profesionales de la salud alrededor del mundo para mejorar la calidad de vida de los más necesitados, ofreciendo un sistema libre que optimice la promoción de la salud y la prevención de la enfermedad. 


Características de GNU Health :


    - Focalizado en medicina familiar y APS (Atención Primaria de la Salud)

    - Interés en condiciones Socio-economicas (estilos de vida, ámbito familiar, educación...)

    - Enfermedades y Procedimientos Médicos standard (ICD-10 / ICD-10-PCS)

    - Gestión de Internación (Hospitalización)

    - Marcadores genéticos y riesgos hereditarios: Más de 4200 genes relacionados con enfermedades

    - Epidemiología y otros registros estadísticos

    - Registro Electrónico. Sin necesidad de papel

    - Recetas

    - Facturación 

    - Administración del Paciente (creación, evaluación / consultas, historia ...)

    - Administración de Laboratorio

    - Vademécum

    - Gestión de Stock y de cadena de abastecimiento

    - Administración Financiera y gestión Hospitalaria

    - Diseñado con los estándares de la industria en mente

    - Software Libre:  License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>

** Para mayor información, visite la página del proyecto en http://health.gnu.org

** Puede escribirnos a health@gnusolidario.org

''',


}
