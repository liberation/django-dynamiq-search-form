# -*- coding: utf-8 -*-

from extended_choices import Choices

from ..constants import (LOOKUP_NEGATIVE_PREFIX, FILTER_LOOKUPS_STR,
                        FILTER_LOOKUPS_INT, FILTER_LOOKUPS_DATE)


QUERY_PLAN = Choices(
    ('LONG', 'long', u'Avec total (+ lent)'),
    ('SHORT', 'short', u'Premiers résultats (rapide)'),
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
