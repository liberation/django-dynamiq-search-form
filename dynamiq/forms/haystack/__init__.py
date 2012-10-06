# -*- coding: utf-8 -*-


from dynamiq.forms.base import AdvancedForm
from .constants import (FILTER_LOOKUPS_FULLTEXT, FILTER_LOOKUPS, FILTER_LOOKUPS_ALIASES)


class HaystackForm(AdvancedForm):

    # Redefine it class level
    FILTER_LOOKUPS_FULLTEXT = FILTER_LOOKUPS_FULLTEXT
    FILTER_LOOKUPS = FILTER_LOOKUPS
    FILTER_LOOKUPS_ALIASES = FILTER_LOOKUPS_ALIASES

    def __init__(self, *args, **kwargs):
        super(HaystackForm, self).__init__(*args, **kwargs)

        # Fulltext lookups are different between SeSQL and Haystack
        self.fields['fulltext_lookup'].extended_choices = self.FILTER_LOOKUPS_FULLTEXT
