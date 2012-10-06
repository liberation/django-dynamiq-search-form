# -*- coding: utf-8 -*-

from extended_choices import Choices
from extended_choices.fields import ExtendedChoiceField

from dynamiq.forms.base import AdvancedForm, ModelSearchOptionsForm
from dynamiq.fields import IntChoiceField
from dynamiq.forms.constants import YES_NO

from .constants import (QUERY_PLAN, FILTER_LOOKUPS_FULLTEXT, FILTER_LOOKUPS,
                        FILTER_LOOKUPS_ALIASES)


class SeSQLOptionsForm(ModelSearchOptionsForm):
    """
    Query plan aware options form.
    """

    QUERY_PLAN = QUERY_PLAN

    query_plan = ExtendedChoiceField(extended_choices=QUERY_PLAN, required=True, initial=QUERY_PLAN.SHORT, label=u"Mode")


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
