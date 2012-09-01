# -*- coding: utf-8 -*-

from django.db.models import Q

from ..utils import StringFiltersBuilder
from .forms.haystack import BoatSearchForm
from .base import DynamiqBaseTests


class StringFiltersBuilderTests(DynamiqBaseTests):

    def test_split_query_string_must_split_on_spaces_unless_in_quotes(self):
        s = """daniel AND country!=FR OR -"Le PEN Marine" country:FR is_active:1 group=NI"""
        output = StringFiltersBuilder.split_query_string(s)
        expected_output = [
            "daniel",
            "AND",
            "country!=FR",
            "OR",
            "-Le PEN Marine",
            "country:FR",
            "is_active:1",
            "group=NI"
        ]
        self.assertEqual(expected_output, output)

    def test_split_query_element(self):
        def do(input, output):
            self.assertEqual(
                StringFiltersBuilder.split_query_element(input),
                output,
            )
        do("daniel", ['daniel'])
        do("AND", ['AND'])
        do("country!=FR", ['country', '!=', 'FR'])
        do("OR", ['OR'])
        do("-Le PEN Marine", ['-Le PEN Marine'])
        do("country:FR", ['country', ':', 'FR'])

    def test_default_filter_is_used_if_not_given(self):
        q = "Spray"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(fulltext__contains="Spray")
        self.assertEqualQ(query, expected)

    def test_simple_search_is_ANDed(self):
        q = "Pen Duick"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(fulltext__contains="Pen") & Q(fulltext__contains="Duick")
        self.assertEqualQ(query, expected)

    def test_search_with_AND_is_ANDed(self):
        q = "Joshua AND Moitessier"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(fulltext__contains="Joshua") & Q(fulltext__contains="Moitessier")
        self.assertEqualQ(query, expected)

    def test_search_with_OR_is_ORed(self):
        q = "Joshua OR Moitessier"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(fulltext__contains="Joshua") | Q(fulltext__contains="Moitessier")
        self.assertEqualQ(query, expected)

    def test_OR_and_AND_can_be_mixed(self):
        q = "Pen Duick OR Commodore Explorer"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        Q1 = Q(fulltext__contains="Pen") & Q(fulltext__contains="Duick")
        Q2 = Q(fulltext__contains="Commodore") & Q(fulltext__contains="Explorer")
        expected = Q1 | Q2
        self.assertEqualQ(query, expected)

    def test_search_field_can_be_defined(self):
        q = "captain:Tabarly"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(captain__contains="Tabarly")
        self.assertEqualQ(query, expected)

    def test_operator_equal_can_be_used(self):
        q = "captain=Tabarly"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(captain__contains="Tabarly")
        self.assertEqualQ(query, expected)

    def test_lookup_can_be_negated_on_operator(self):
        q = "captain!=Tabarly"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = ~Q(captain__contains="Tabarly")
        self.assertEqualQ(query, expected)
        q = "captain!:Tabarly"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = ~Q(captain__contains="Tabarly")
        self.assertEqualQ(query, expected)

    def test_lookup_can_be_negated_on_value(self):
        q = "-Tabarly"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = ~Q(fulltext__contains="Tabarly")
        self.assertEqualQ(query, expected)

    def test_quoted_terms_are_not_splited(self):
        q = '"Eric Tabarly"'
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(fulltext__contains="Eric Tabarly")
        self.assertEqualQ(query, expected)

    def test_gte_can_be_used(self):
        q = 'year>=1966'
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(year__gte="1966")
        self.assertEqualQ(query, expected)

    def test_lte_can_be_used(self):
        q = 'year<=1966'
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(year__lte="1966")
        self.assertEqualQ(query, expected)

    def test_gte_and_lte_can_be_mixed(self):
        q = 'year>=1966 year<=1978'
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        expected = Q(year__gte="1966") & Q(year__lte="1978")
        self.assertEqualQ(query, expected)

    def test_complex_search(self):
        q = "captain:Tabarly year>=1966 mast=1 OR captain!=Cammas year<=1999 OR captain='Bernard Moitessier' Joshua"
        F = StringFiltersBuilder(q, BoatSearchForm)
        query, label = F()
        Q1 = Q(captain__contains="Tabarly") & Q(year__gte="1966") & Q(mast="1")
        Q2 = ~Q(captain__contains="Cammas") & Q(year__lte="1999")
        Q3 = Q(captain__contains="Bernard Moitessier") & Q(fulltext__contains="Joshua")
        expected = Q1 | Q2 | Q3
        self.assertEqualQ(query, expected)
