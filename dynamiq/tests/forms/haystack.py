# -*- coding: utf-8 -*-

from extended_choices import Choices

from dynamiq.forms.haystack import HaystackForm
from dynamiq.forms.base import DynamiqSearchOptionsForm, DynamiqAdvancedFormset
from dynamiq.fields import DynamiqStrChoiceField


KIND = Choices(
    ('SAIL', 'sail', 'Sailboat'),
    ('MOTOR', 'motor', 'Motorboat'),
)

FILTER_NAME = Choices(
    ('FULLTEXT', 'fulltext', u'Name'),
    ('CAPTAIN', 'captain', u'Captain'),
    ('LENGTH', 'length', u'Length'),
    ('YEAR', 'year', u'Construction year'),
    ('HULL', 'hull', u'Number of hulls'),
    ('MAST', 'mast', u'Number of masts'),
    ('KIND', 'kind', u'Kind of boat'),
    ('ACTIVE', 'active', u'Still active'),
)

SORT_CHOICES = Choices(
    ('YEAR', '-year', u'Construction year'),
    ('YEAR_ASC', 'year', u'Construction year asc'),
)


class BoatSearchOptionsForm(DynamiqSearchOptionsForm):

    SORT = SORT_CHOICES
    SORT_INITIAL = SORT.YEAR


class BoatSearchForm(HaystackForm):
    options_form_class = BoatSearchOptionsForm

    FILTER_NAME = FILTER_NAME

    _FILTERS_BY_FIELD = {
        FILTER_NAME.FULLTEXT: {
            'type': 'fulltext',
            'receptacle': 'fulltext'
        },
        FILTER_NAME.CAPTAIN: {
            'type': 'fulltext',
            'receptacle': 'fulltext'
        },
        FILTER_NAME.LENGTH: {
            'type': 'int',
            'receptacle': 'int'
        },
        FILTER_NAME.KIND: {
            'type': 'str',
            'receptacle': 'kind'
        },
        FILTER_NAME.YEAR: {
            'type': 'date',
            'receptacle': 'date'
        },
        FILTER_NAME.HULL: {
            'type': 'int',
            'receptacle': 'int'
        },
        FILTER_NAME.MAST: {
            'type': 'int',
            'receptacle': 'int'
        },
        FILTER_NAME.ACTIVE: {
            'type': 'yes_no',
            'receptacle': 'yes_no'
        },
    }
    filter_value_kind = DynamiqStrChoiceField(KIND)


class BoatSearchAdvancedFormset(DynamiqAdvancedFormset):
    options_form_class = BoatSearchOptionsForm
    form = BoatSearchForm
