# -*- coding: utf-8 -*-

from extended_choices import Choices

from dynamiq.forms.haystack import HaystackForm
from dynamiq.forms.base import SearchOptionsForm, AdvancedFormset
from dynamiq.fields import StrChoiceField, IntChoiceField


KIND = Choices(
    ('SAIL', 'sail', 'Sailboat'),
    ('MOTOR', 'motor', 'Motorboat'),
)

RIGGING = Choices(
    ('SLOOP', 1, 'Sloop'),
    ('CUTTER', 2, 'Cutter'),
    ('KETCH', 3, 'Ketch'),
    ('SCHOONER', 4, 'Shooner'),
)

FILTER_NAME = Choices(
    ('FULLTEXT', 'fulltext', u'Name'),
    ('CAPTAIN', 'captain', u'Captain'),
    ('LENGTH', 'length', u'Length'),
    ('YEAR', 'year', u'Construction year'),
    ('HULL', 'hull', u'Number of hulls'),
    ('MAST', 'mast', u'Number of masts'),
    ('KIND', 'kind', u'Kind of boat'),
    ('RIGGING', 'rigging', u'Rigging of the sailboat'),
    ('ACTIVE', 'active', u'Still active'),
)

SORT_CHOICES = Choices(
    ('YEAR', '-year', u'Construction year'),
    ('YEAR_ASC', 'year', u'Construction year asc'),
)


class BoatSearchOptionsForm(SearchOptionsForm):

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
        FILTER_NAME.RIGGING: {
            'type': 'id',
            'receptacle': 'rigging'
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
    filter_value_kind = StrChoiceField(KIND)
    filter_value_rigging = IntChoiceField(RIGGING)


class BoatSearchAdvancedFormset(AdvancedFormset):
    options_form_class = BoatSearchOptionsForm
    form = BoatSearchForm
