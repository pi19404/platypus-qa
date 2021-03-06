# coding=utf-8
"""
Copyright (c) 2017 Lexistems SAS and École normale supérieure de Lyon

This file is part of Platypus.

Platypus is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import sys
import unittest
from itertools import chain

from platypus_qa.analyzer.grammatical_analyzer import GrammaticalAnalyzer
from platypus_qa.database.formula import Select, VariableFormula, TripleFormula, ValueFormula, EqualityFormula, \
    ExistsFormula
from platypus_qa.database.owl import ObjectProperty, DatatypeProperty, owl_NamedIndividual, Class, NamedIndividual, \
    xsd_dateTime, xsd_decimal, XSDDateTimeLiteral, schema_Person, schema_Place, geo_wktLiteral
from platypus_qa.nlp.core_nlp import CoreNLPParser
from tests.simple_knowledge_model import SimpleKnowledgeBase

_schema_Country = Class('http://schema.org/Place', (owl_NamedIndividual, schema_Place))
_schema_Movie = Class('http://schema.org/Movie', (owl_NamedIndividual,))
_schema_CreativeWork = Class('http://schema.org/CreativeWork', (owl_NamedIndividual,))
_schema_Book = Class('http://schema.org/Book', (owl_NamedIndividual, _schema_CreativeWork))

_individuals = {
    'Francia': [_schema_Country],
    'Reino Unido': [_schema_Country],
    'Homer J. Simpson': [schema_Person],
    'Bob Marley': [schema_Person],
    'guepardo': [owl_NamedIndividual],
    'Barack Obama': [schema_Person],
    'Big Ben': [schema_Place],
    'I, Robot': [_schema_Movie],
    'Robin Hood': [_schema_Movie],
    'avión': [owl_NamedIndividual],
    'varones': [owl_NamedIndividual],
    'Lyon': [schema_Place],
    'Paris': [schema_Place],
    'tenedor': [owl_NamedIndividual],
    'ciudad': [owl_NamedIndividual],
    'El Principito': [_schema_Book],
    'Vol de Nuit': [_schema_Book],
    'Douglas': [owl_NamedIndividual],
    'fresa': [owl_NamedIndividual]
}

_object_properties = {
    'hija': schema_Person,
    'primer ministro': schema_Person,
    'presidente': schema_Person,
    'hijos': schema_Person,
    'niños': schema_Person,
    'lugar de nacimiento': schema_Place,
    'esposa': schema_Person,
    'marido': schema_Person,
    'actor principal': schema_Person,
    'capital': schema_Place,
    'piloto': schema_Person,
    'libros': owl_NamedIndividual,
    'escrito por': schema_Person,
    'origen': owl_NamedIndividual,
    'autor': schema_Person,
    'tipo': owl_NamedIndividual,
    'nombre': owl_NamedIndividual
}

_data_properties = {
    'fecha de nacen': xsd_dateTime,
    'fecha de nacimiento': xsd_dateTime,
    'velocidad': xsd_decimal,
    'edad': xsd_decimal,
    'ancho': xsd_decimal,
    'altura': xsd_decimal,
    'nació en': xsd_dateTime,
    'ubicación': geo_wktLiteral,
}


def _get_individual(label: str) -> ValueFormula:
    return ValueFormula(NamedIndividual(label, _individuals[label]))


def _get_property(label: str) -> ValueFormula:
    if label in _object_properties:
        return ValueFormula(ObjectProperty(label, range=_object_properties[label]))
    if label in _data_properties:
        return ValueFormula(DatatypeProperty(label, range=_data_properties[label]))


_knowledge_base = SimpleKnowledgeBase(
    {label: [_get_individual(label).term] for label in _individuals.keys()},
    {label: [_get_property(label).term] for label in chain(_data_properties.keys(), _object_properties.keys())},
    [ObjectProperty('tipo', range=owl_NamedIndividual)]
)

_x = VariableFormula('x')
_y = VariableFormula('y')
_z = VariableFormula('z')
logging.basicConfig(level=logging.DEBUG)

_parsed_sentences = {
    'Barack Obama':
        Select(_x, EqualityFormula(_x, _get_individual('Barack Obama'))),

    'El Bob Marley':
        Select(_x, EqualityFormula(_x, _get_individual('Bob Marley'))),

    '¿Quién es Barack Obama?':
        Select(_x, EqualityFormula(_x, _get_individual('Barack Obama'))),

    'hija de Barack Obama':
        Select(_x, TripleFormula(_get_individual('Barack Obama'), _get_property('hija'), _x)),

    'El primer ministro de Francia':
        Select(_x, TripleFormula(_get_individual('Francia'), _get_property('primer ministro'), _x)),

    '¿Quién es el primer ministro de Francia?':
        Select(_x, TripleFormula(_get_individual('Francia'), _get_property('primer ministro'), _x)),

    '¿Quién es el presidente del Reino Unido':
        Select(_x, TripleFormula(_get_individual('Reino Unido'), _get_property('presidente'), _x)),

    '¿Quién es el presidente de Francia?':
        Select(_x, TripleFormula(_get_individual('Francia'), _get_property('presidente'), _x)),

    '¿Cuál es la velocidad del guepardo?':
        Select(_x, TripleFormula(_get_individual('guepardo'), _get_property('velocidad'), _x)),

    '¿Cuáles son los hijos de la esposa de Barack Obama?':
        Select(_x, ExistsFormula(_y, TripleFormula(_get_individual('Barack Obama'), _get_property('esposa'), _y) &
                                 TripleFormula(_y, _get_property('hijos'), _x))),

    '¿Cuál es el ancho de un guepardo?':
        Select(_x, TripleFormula(_get_individual('guepardo'), _get_property('ancho'), _x)),

    '¿Cuánto es la altura del Big Ben?':
        Select(_x, TripleFormula(_get_individual('Big Ben'), _get_property('altura'), _x)),

    '¿Qué es un tenedor?':
        Select(_x, EqualityFormula(_x, _get_individual('tenedor'))),

    '¿Qué es "I, Robot"?':
        Select(_x, EqualityFormula(_x, _get_individual('I, Robot'))),

    '¿Qué es Robin Hood?':
        Select(_x, EqualityFormula(_x, _get_individual('Robin Hood'))),

    'Daños el primer ministro de Francia.':
        Select(_x, TripleFormula(_get_individual('Francia'), _get_property('primer ministro'), _x)),

    'libros de Barack Obama':
        Select(_x, TripleFormula(_get_individual('Barack Obama'), _get_property('libros'), _x)),

    'Lista de libros de Barack Obama':
        Select(_x, TripleFormula(_get_individual('Barack Obama'), _get_property('libros'), _x)),

    '¿Cuál es la ubicación de Big Ben?':
        Select(_x, TripleFormula(_get_individual('Big Ben'), _get_property('ubicación'), _x)),

    '¿Dónde está el Big Ben?':
        Select(_x, TripleFormula(_get_individual('Big Ben'), _get_property('ubicación'), _x)),

    '¿Dónde está Lyon?':
        Select(_x, TripleFormula(_get_individual('Lyon'), _get_property('ubicación'), _x)),

    '¿Dónde está Paris?':
        Select(_x, TripleFormula(_get_individual('Paris'), _get_property('ubicación'), _x)),

    '¿Quién nació en 1960?':
        Select(_x,
               TripleFormula(_x, _get_property('nació en'), ValueFormula(XSDDateTimeLiteral(1960, 0, 0, 0, 0, 0))))
}

"""
    '¿Cuál es la fecha de nacimiento de Bob Marley?':
        Function(_x, TripleFormula(_get_individual('Bob Marley'), _get_property('fecha de nacimiento'), _x)),

    'El lugar de nacimiento del presidente de Francia':
        Function(_x, ExistsFormula(_y, TripleFormula(_get_individual('Francia'), _get_property('presidente'), _y) &
                                   TripleFormula(_y, _get_property('lugar de nacimiento'), _x))),

    '¿Cuáles son los hijos varones de Barack Obama?':
        Function(_x, TripleFormula(_get_individual('Barack Obama'), _get_property('hijos'), _x) &
                 TripleFormula(_x, _get_property('tipo'), _get_individual('varones'))),

    'Cuándo nació el presidente de Francia?':
        Function(_x, ExistsFormula(_y, TripleFormula(_get_individual('Francia'), _get_property('presidente'), _y) &
                                   TripleFormula(_y, _get_property('fecha de nacimiento'), _x))),

    'Cuándo los niños nacen del presidente de Francia?':
        Function(_x, ExistsFormula(_y, ExistsFormula(_z,
                                                     TripleFormula(_get_individual('Francia'),
                                                                   _get_property('presidente'), _z) &
                                                     TripleFormula(_z, _get_property('niños'), _y)) &
                                   TripleFormula(_y, _get_property('fecha de nacimiento'), _x))),                                
"""


class SpanishGrammaticalAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self._analyzer = GrammaticalAnalyzer(
            CoreNLPParser(['https://corenlp.askplatyp.us/1.7/']), _knowledge_base, 'es')

    def testParsing(self):
        bad_count = 0
        for (sentence, expected_formula) in _parsed_sentences.items():
            returned_formulas = self._analyzer.analyze(sentence)
            correct_count = len(returned_formulas)
            for formula in returned_formulas:
                try:
                    self.assertEqual(formula, expected_formula)
                except AssertionError:
                    correct_count -= 1
            if not correct_count:
                print(
                    '[es_grammatical_analyzer test] The following question check failed: {}\nExpected: {}\nActual: {}'.format(
                        sentence, expected_formula, ', '.join(str(formula) for formula in returned_formulas)),
                    file=sys.stderr)
                bad_count += 1
        if bad_count > 0:
            raise AssertionError('{} on {} tests failed'.format(bad_count, len(_parsed_sentences)))
