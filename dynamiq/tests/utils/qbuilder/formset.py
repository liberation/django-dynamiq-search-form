# -*- coding: utf-8 -*-

from django.db.models import Q

from dynamiq.tests.forms.haystack import BoatSearchForm, BoatSearchAdvancedFormset
from dynamiq.tests.base import BaseFormsetQBuilderTests


class FormsetQBuilderTests(BaseFormsetQBuilderTests):

    formset = BoatSearchAdvancedFormset
    form = BoatSearchForm

    def test_simple_fulltext_search(self):
        data = [
            {
                'filter_name': 'captain',
                'fulltext_lookup': BoatSearchForm.FILTER_LOOKUPS_FULLTEXT.CONTAINS,
                'filter_value_fulltext': u'Tabarly',
            }
        ]
        expected = Q(captain__contains=u"Tabarly")
        self.run_test(data, expected)

    def test_filters_can_be_ANDed(self):
        data = [
            {
                'filter_name': 'captain',
                'fulltext_lookup': BoatSearchForm.FILTER_LOOKUPS_FULLTEXT.CONTAINS,
                'filter_value_fulltext': u'Tabarly',
                'filter_right_op': BoatSearchForm.FILTER_RIGHT_OP.AND,
            },
            {
                'filter_name': 'mast',
                'int_lookup': BoatSearchForm.FILTER_LOOKUPS_INT.EXACT,
                'filter_value_int': 1,
            }
        ]
        expected = Q(captain__contains=u"Tabarly") & Q(mast=1)
        self.run_test(data, expected)

    def test_filters_can_be_ORed(self):
        data = [
            {
                'filter_name': 'captain',
                'fulltext_lookup': BoatSearchForm.FILTER_LOOKUPS_FULLTEXT.CONTAINS,
                'filter_value_fulltext': u'Tabarly',
                'filter_right_op': BoatSearchForm.FILTER_RIGHT_OP.OR,
            },
            {
                'filter_name': 'captain',
                'fulltext_lookup': BoatSearchForm.FILTER_LOOKUPS_FULLTEXT.CONTAINS,
                'filter_value_fulltext': u'Moitessier',
            }
        ]
        expected = Q(captain__contains=u"Tabarly") | Q(captain__contains=u"Moitessier")
        self.run_test(data, expected)

    def test_OR_and_AND_can_be_mixed(self):
        data = [
            {
                'filter_name': 'captain',
                'fulltext_lookup': BoatSearchForm.FILTER_LOOKUPS_FULLTEXT.CONTAINS,
                'filter_value_fulltext': u'Didier',
                'filter_right_op': BoatSearchForm.FILTER_RIGHT_OP.AND,
            },
            {
                'filter_name': 'captain',
                'fulltext_lookup': BoatSearchForm.FILTER_LOOKUPS_FULLTEXT.CONTAINS,
                'filter_value_fulltext': u'Peyron',
                'filter_right_op': BoatSearchForm.FILTER_RIGHT_OP.OR,
            },
            {
                'filter_name': 'captain',
                'fulltext_lookup': BoatSearchForm.FILTER_LOOKUPS_FULLTEXT.CONTAINS,
                'filter_value_fulltext': u'Moitessier',
            }
        ]
        Q1 = Q(captain__contains=u"Didier") & Q(captain__contains=u"Peyron")
        expected = Q1 | Q(captain__contains=u"Moitessier")
        self.run_test(data, expected)
