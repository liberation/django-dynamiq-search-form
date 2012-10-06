# -*- coding: utf-8 -*-

from extended_choices import Choices
from extended_choices.fields import ExtendedChoiceField

from dynamiq.forms.base import AdvancedForm, SearchOptionsForm
from dynamiq.fields import CommaSeparatedChoiceField, IntChoiceField
from dynamiq.forms.constants import YES_NO

from .constants import (QUERY_PLAN, FILTER_LOOKUPS_FULLTEXT, FILTER_LOOKUPS,
                        FILTER_LOOKUPS_ALIASES)


class SeSQLOptionsForm(SearchOptionsForm):
    """
    Query plan and model aware options form.
    """

    QUERY_PLAN = QUERY_PLAN
    MODEL = ()
    MODEL_INITIAL = None
    MODEL_OPTIONS = {
         # MODEL_CHOICES.GROUP: {
         #     'filters': ('TITLE', ),  # available filters for this model
         #     'sort': ('RELEVANCE', 'LAST_PUBLISHED', ),  # available sort options for this model
         # },
     }

    model = CommaSeparatedChoiceField(extended_choices=Choices(), required=True)
    query_plan = ExtendedChoiceField(extended_choices=QUERY_PLAN, required=True, initial=QUERY_PLAN.SHORT, label=u"Mode")

    def __init__(self, *args, **kwargs):
        super(SeSQLOptionsForm, self).__init__(*args, **kwargs)

        self.fields['model'].extended_choices = self.MODEL
        self.fields['model'].initial = self.MODEL_INITIAL


class SeSQLForm(AdvancedForm):

    # Redefine it at class level
    FILTER_LOOKUPS_FULLTEXT = FILTER_LOOKUPS_FULLTEXT
    FILTER_LOOKUPS = FILTER_LOOKUPS
    FILTER_LOOKUPS_ALIASES = FILTER_LOOKUPS_ALIASES

    # SeSQL doesn't handle boolean fields, it saves them as 1 or 0.
    filter_value_yes_no = IntChoiceField(YES_NO)

    def __init__(self, *args, **kwargs):
        super(SeSQLForm, self).__init__(*args, **kwargs)

        # Fulltext lookups are different between SeSQL and Haystack
        self.fields['fulltext_lookup'].extended_choices = self.FILTER_LOOKUPS_FULLTEXT
