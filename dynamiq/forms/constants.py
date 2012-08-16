# -*- coding: utf-8 -*-

from extended_choices import Choices

YES_NO = Choices(
    ('YES', 1, 'Oui'),
    ('NO', 0, 'Non'),
)

FILTER_RIGHT_OP = Choices(
    ('EMPTY', '', ''),
    ('AND', 'AND', u'ET'),
    ('OR', 'OR', u'OU'),
)

LOOKUP_NEGATIVE_PREFIX = 'not_'

FILTER_LOOKUPS_STR = Choices(
    ('EXACT', 'exact', 'est'),
    ('NOT_EXACT', LOOKUP_NEGATIVE_PREFIX + 'exact', 'n\'est pas'),
)

FILTER_LOOKUPS_INT = Choices(
    ('EXACT', 'exact', 'est'),
    ('NOT_EXACT', LOOKUP_NEGATIVE_PREFIX + 'exact', 'n\'est pas'),
    ('GTE', 'gte', u'supérieure à'),
    ('LTE', 'lte', u'inférieure à'),
    # ('BETWEEN', 'between', 'entre'), TODO
)

FILTER_LOOKUPS_DATE = Choices(
    ('RELATIVE', 'relative', 'depuis'),
    ('EXACT', 'exact', 'est'),
    ('GTE', 'gte', u'supérieure à'),
    ('LTE', 'lte', u'inférieure à'),
    ('BETWEEN', 'between', 'entre'),
)

FILTER_DATE_RELATIVE = Choices(
    ('TODAY', 0, 'Aujourd\'hui'),
    ('YESTERDAY', 1, 'Hier'),
    ('THREE_DAYS', 3, 'Trois jours'),
    ('SEVEN_DAYS', 7, 'Une semaine'),
    ('SIX_MONTHS', 180, 'Six mois'),
    ('ONE_YEAR', 365, 'Un an'),
    ('TWO_YEARS', 730, 'Deux ans'),
    ('TOMORROW', -1, 'Demain'),
)

FILTER_LOOKUPS_FULLTEXT = Choices(
    ('CONTAINS', 'containswords', 'contient'),
    ('EXACT', 'containsexact', 'contient exactement'),
    ('NOT_CONTAINS', LOOKUP_NEGATIVE_PREFIX + 'containswords', 'ne contient pas')
)

FILTER_LOOKUPS = {
    'fulltext': FILTER_LOOKUPS_FULLTEXT,
    'str': FILTER_LOOKUPS_STR,
    'int': FILTER_LOOKUPS_INT,
    'date': FILTER_LOOKUPS_DATE,
}
