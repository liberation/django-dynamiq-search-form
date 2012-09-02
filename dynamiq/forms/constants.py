# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from extended_choices import Choices

YES_NO = Choices(
    ('YES', 1, _('yes')),
    ('NO', 0, _('no')),
)

FILTER_RIGHT_OP = Choices(
    ('EMPTY', '', ''),
    ('AND', 'AND', _('AND')),
    ('OR', 'OR', _('OR')),
)

LOOKUP_NEGATIVE_PREFIX = 'not_'

FILTER_LOOKUPS_STR = Choices(
    ('EXACT', 'exact', _('is')),
    ('NOT_EXACT', LOOKUP_NEGATIVE_PREFIX + 'exact', _("is not")),
)

FILTER_LOOKUPS_YES_NO = Choices(
    ('EXACT', 'exact', _('is')),
    ('NOT_EXACT', LOOKUP_NEGATIVE_PREFIX + 'exact', _('is not')),
)

FILTER_LOOKUPS_INT = Choices(
    ('EXACT', 'exact', _('is')),
    ('NOT_EXACT', LOOKUP_NEGATIVE_PREFIX + 'exact', _('is not')),
    ('GTE', 'gte', _('greather than or equal to')),
    ('LTE', 'lte', _('lower than or equal to')),
    # ('BETWEEN', 'between', 'entre'), TODO
)

FILTER_LOOKUPS_DATE = Choices(
    ('RELATIVE', 'relative', _('from')),
    ('EXACT', 'exact', _('is')),
    ('GTE', 'gte', _('greather than or equal to')),
    ('LTE', 'lte', _('lower than or equal to')),
    ('BETWEEN', 'between', _('between')),
)

FILTER_DATE_RELATIVE = Choices(
    ('TODAY', 0, _('today')),
    ('YESTERDAY', 1, _('yesterday')),
    ('THREE_DAYS', 3, _('three days')),
    ('SEVEN_DAYS', 7, _('one week')),
    ('SIX_MONTHS', 180, _('six months')),
    ('ONE_YEAR', 365, _('one year')),
    ('TWO_YEARS', 730, _('two years')),
    ('TOMORROW', -1, _('tomorrow')),
)

FILTER_LOOKUPS_FULLTEXT = Choices(
    ('CONTAINS', 'containswords', _('contains')),
    ('EXACT', 'containsexact', _('contains exactly')),
    ('NOT_CONTAINS', LOOKUP_NEGATIVE_PREFIX + 'containswords', _('does not contain'))
)

FILTER_LOOKUPS = {
    'fulltext': FILTER_LOOKUPS_FULLTEXT,
    'str': FILTER_LOOKUPS_STR,
    'int': FILTER_LOOKUPS_INT,
    'date': FILTER_LOOKUPS_DATE,
    'yes_no': FILTER_LOOKUPS_YES_NO,
}

# Put generic ones at first level,
# and type specific in type key
FILTER_LOOKUPS_ALIASES = {
    "=": 'exact',
    ':': 'exact',
    "!=": LOOKUP_NEGATIVE_PREFIX + 'exact',
    '!:': LOOKUP_NEGATIVE_PREFIX + 'exact',
    '>=': 'gte',
    '<=': 'lte',
    'fulltext': {
        "=": 'containswords',
        ':': 'containswords',
        "!=": LOOKUP_NEGATIVE_PREFIX + 'containswords',
        '!:': LOOKUP_NEGATIVE_PREFIX + 'containswords',
    },
}
