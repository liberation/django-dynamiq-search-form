# -*- coding: utf-8 -*-


from dynamiq.forms.base import DynamiqAdvancedForm
from .constants import (FILTER_LOOKUPS_FULLTEXT, FILTER_LOOKUPS)


class HaystackForm(DynamiqAdvancedForm):

    def __init__(self, *args, **kwargs):
        super(HaystackForm, self).__init__(*args, **kwargs)

        # Fulltext lookups are different between SeSQL and Haystack
        self.FILTER_LOOKUPS_FULLTEXT = FILTER_LOOKUPS_FULLTEXT
        self.FILTER_LOOKUPS = FILTER_LOOKUPS
        self.fields['fulltext_lookup'].extended_choices = self.FILTER_LOOKUPS_FULLTEXT
