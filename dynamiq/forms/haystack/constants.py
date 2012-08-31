# -*- coding: utf-8 -*-

from extended_choices import Choices

from ..constants import LOOKUP_NEGATIVE_PREFIX
from ..constants import FILTER_LOOKUPS as DEFAULT_FILTER_LOOKUPS


FILTER_LOOKUPS_FULLTEXT = Choices(
    ('CONTAINS', 'contains', 'contient'),
    ('EXACT', 'exact', 'contient exactement'),
    ('NOT_CONTAINS', LOOKUP_NEGATIVE_PREFIX + 'contains', 'ne contient pas')
)

FILTER_LOOKUPS = dict(DEFAULT_FILTER_LOOKUPS)
FILTER_LOOKUPS.update({
    'fulltext': FILTER_LOOKUPS_FULLTEXT,
})
