from django.utils.unittest import TestCase

from ..utils import (get_advanced_search_formset_class, FormsetQBuilder,
                     ParsedStringQBuilder)


class BaseTests(TestCase):

    def assertEqualQ(self, Q1, Q2):
        self.assertEqual(str(Q1), str(Q2))


class BaseStringParsedQBuilderTests(BaseTests):

    form = None

    def run_test(self, q, expected):
        F = ParsedStringQBuilder(q, self.form)
        query, label = F()
        self.assertEqualQ(query, expected)


class BaseFormsetQBuilderTests(BaseTests):
    """
    Inherite from this class for testing formsets.
    Just define formset and form.
    And use run_test to test your datas.
    """

    formset = None
    form = None

    def run_test(self, data, expected):
        """
        `data` here is a list of dicts, each reprensenting the data of a form
        of the formset.
        Ex.:
        data = [{
            'filter_name': 'captain',
            'fulltext_lookup': 'exact',
            'filter_value_fulltext': u'Tabarly',
        }]
        `expected` is a Q object.
        """
        data = self.build_data(data)
        formset_class = get_advanced_search_formset_class(None, self.formset, self.form)
        formset = formset_class(data)
        formset.full_clean()
        if formset.is_valid():
            F = FormsetQBuilder(formset)
            query, label = F()
        else:
            self.fail(formset.errors)
        self.assertEqualQ(query, expected)

    def build_data(self, data):
        """
        Build data needed to instantiate a formset from a set of form datas.
        """
        formset_data = {
            'form-TOTAL_FORMS': 0,  # Will be updated at the end
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': '',
            'sort': self.formset.options_form_class.SORT.YEAR,
            'limit': 15,
        }
        total_form = 0
        for idx, form_data in enumerate(data):
            total_form += 1
            for key, value in form_data.iteritems():
                formset_data.update({
                    'form-%d-%s' % (idx, key): value
                })
        formset_data['form-TOTAL_FORMS'] = total_form
        return formset_data
