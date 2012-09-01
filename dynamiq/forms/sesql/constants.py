# -*- coding: utf-8 -*-

from extended_choices import Choices

from ..constants import LOOKUP_NEGATIVE_PREFIX
from ..constants import FILTER_LOOKUPS as DEFAULT_FILTER_LOOKUPS
from ..constants import FILTER_LOOKUPS_ALIASES as DEFAULT_FILTER_LOOKUPS_ALIASES


QUERY_PLAN = Choices(
    ('LONG', 'long', u'Avec total (+ lent)'),
    ('SHORT', 'short', u'Premiers résultats (rapide)'),
)

FILTER_LOOKUPS_FULLTEXT = Choices(
    ('CONTAINS', 'containswords', 'contient'),
    ('EXACT', 'containsexact', 'contient exactement'),
    ('NOT_CONTAINS', LOOKUP_NEGATIVE_PREFIX + 'containswords', 'ne contient pas')
)

FILTER_LOOKUPS = dict(DEFAULT_FILTER_LOOKUPS)
FILTER_LOOKUPS.update({
    'fulltext': FILTER_LOOKUPS_FULLTEXT,
})
FILTER_LOOKUPS_ALIASES = dict(DEFAULT_FILTER_LOOKUPS_ALIASES)
FILTER_LOOKUPS_ALIASES.update({
    'fulltext': {
        '=': 'containswords',
        ':': 'containswords',
        "!=": LOOKUP_NEGATIVE_PREFIX + 'containswords',
        '!:': LOOKUP_NEGATIVE_PREFIX + 'containswords',
    },
})
