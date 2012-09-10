# -*- coding: utf-8 -*-

from django.db.models import Q

from dynamiq.tests.forms.haystack import BoatSearchForm, BoatSearchAdvancedFormset
from dynamiq.tests.base import BaseFormsetQBuilderTests


class BoatFormsetBaseTest(BaseFormsetQBuilderTests):

    formset = BoatSearchAdvancedFormset
    form = BoatSearchForm


class FormsetQBuilderTests(BoatFormsetBaseTest):

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


class IntLookupTests(BoatFormsetBaseTest):

    def test_exact_lookup(self):
        data = [
            {
                'filter_name': 'mast',
                'int_lookup': BoatSearchForm.FILTER_LOOKUPS_INT.EXACT,
                'filter_value_int': 1,
            }
        ]
        expected = Q(mast=1)
        self.run_test(data, expected)

    def test_not_exact_lookup(self):
        data = [
            {
                'filter_name': 'mast',
                'int_lookup': BoatSearchForm.FILTER_LOOKUPS_INT.NOT_EXACT,
                'filter_value_int': 1,
            }
        ]
        expected = ~Q(mast=1)
        self.run_test(data, expected)

    def test_gt_lookup(self):
        data = [
            {
                'filter_name': 'mast',
                'int_lookup': BoatSearchForm.FILTER_LOOKUPS_INT.GT,
                'filter_value_int': 1,
            }
        ]
        expected = Q(mast__gt=1)
        self.run_test(data, expected)

    def test_gte_lookup(self):
        data = [
            {
                'filter_name': 'mast',
                'int_lookup': BoatSearchForm.FILTER_LOOKUPS_INT.GTE,
                'filter_value_int': 1,
            }
        ]
        expected = Q(mast__gte=1)
        self.run_test(data, expected)

    def test_lt_lookup(self):
        data = [
            {
                'filter_name': 'mast',
                'int_lookup': BoatSearchForm.FILTER_LOOKUPS_INT.LT,
                'filter_value_int': 1,
            }
        ]
        expected = Q(mast__lt=1)
        self.run_test(data, expected)

    def test_lte_lookup(self):
        data = [
            {
                'filter_name': 'mast',
                'int_lookup': BoatSearchForm.FILTER_LOOKUPS_INT.LTE,
                'filter_value_int': 1,
            }
        ]
        expected = Q(mast__lte=1)
        self.run_test(data, expected)


class StrLookupTests(BoatFormsetBaseTest):

    def test_exact_lookup(self):
        data = [
            {
                'filter_name': 'kind',
                'str_lookup': BoatSearchForm.FILTER_LOOKUPS_STR.EXACT,
                'filter_value_kind': 'sail',
            }
        ]
        expected = Q(kind="sail")
        self.run_test(data, expected)

    def test_not_exact_lookup(self):
        data = [
            {
                'filter_name': 'kind',
                'str_lookup': BoatSearchForm.FILTER_LOOKUPS_STR.NOT_EXACT,
                'filter_value_kind': 'sail',
            }
        ]
        expected = ~Q(kind="sail")
        self.run_test(data, expected)


class YesNoLookupTests(BoatFormsetBaseTest):

    def test_exact_lookup(self):
        data = [
            {
                'filter_name': 'active',
                'yes_no_lookup': BoatSearchForm.FILTER_LOOKUPS_YES_NO.EXACT,
                'filter_value_yes_no': True,
            }
        ]
        expected = Q(active=True)
        self.run_test(data, expected)
        data = [
            {
                'filter_name': 'active',
                'yes_no_lookup': BoatSearchForm.FILTER_LOOKUPS_YES_NO.EXACT,
                'filter_value_yes_no': False,
            }
        ]
        expected = Q(active=False)
        self.run_test(data, expected)

    def test_not_exact_lookup(self):
        data = [
            {
                'filter_name': 'active',
                'yes_no_lookup': BoatSearchForm.FILTER_LOOKUPS_YES_NO.NOT_EXACT,
                'filter_value_yes_no': True,
            }
        ]
        expected = ~Q(active=True)
        self.run_test(data, expected)
        data = [
            {
                'filter_name': 'active',
                'yes_no_lookup': BoatSearchForm.FILTER_LOOKUPS_YES_NO.NOT_EXACT,
                'filter_value_yes_no': False,
            }
        ]
        expected = ~Q(active=False)
        self.run_test(data, expected)


class IDLookupTests(BoatFormsetBaseTest):

    def test_exact_lookup(self):
        data = [
            {
                'filter_name': 'rigging',
                'id_lookup': BoatSearchForm.FILTER_LOOKUPS_ID.EXACT,
                'filter_value_rigging': 2,
            }
        ]
        expected = Q(rigging=2)
        self.run_test(data, expected)

    def test_not_exact_lookup(self):
        data = [
            {
                'filter_name': 'rigging',
                'id_lookup': BoatSearchForm.FILTER_LOOKUPS_ID.NOT_EXACT,
                'filter_value_rigging': 2,
            }
        ]
        expected = ~Q(rigging=2)
        self.run_test(data, expected)
