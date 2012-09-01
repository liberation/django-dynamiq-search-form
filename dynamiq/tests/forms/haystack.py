# -*- coding: utf-8 -*-

from extended_choices import Choices

from dynamiq.forms.haystack import HaystackForm
from dynamiq.forms.haystack.constants import FILTER_LOOKUPS_ALIASES
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

    _FILTER_TYPE_BY_NAME = {
        FILTER_NAME.FULLTEXT: 'fulltext',
        FILTER_NAME.CAPTAIN: 'fulltext',
        FILTER_NAME.LENGTH: 'int',
        FILTER_NAME.KIND: 'str',
        FILTER_NAME.YEAR: 'date',
        FILTER_NAME.HULL: 'int',
        FILTER_NAME.MAST: 'int',
        FILTER_NAME.ACTIVE: 'yes_no',
    }
    _FILTER_VALUE_RECEPTACLE_BY_NAME = {
        FILTER_NAME.FULLTEXT: 'fulltext',
        FILTER_NAME.CAPTAIN: 'fulltext',
        FILTER_NAME.LENGTH: 'int',
        FILTER_NAME.KIND: 'kind',
        FILTER_NAME.YEAR: 'date',
        FILTER_NAME.HULL: 'int',
        FILTER_NAME.MAST: 'int',
        FILTER_NAME.ACTIVE: 'yes_no',
    }
    FILTER_LOOKUPS_ALIASES = FILTER_LOOKUPS_ALIASES
    filter_value_kind = DynamiqStrChoiceField(KIND)


class BoatSearchAdvancedFormset(DynamiqAdvancedFormset):
    options_form_class = BoatSearchOptionsForm
    form = BoatSearchForm
