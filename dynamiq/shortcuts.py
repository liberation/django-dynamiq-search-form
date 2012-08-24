# -*- coding: utf-8 -*-

from django.utils.http import urlencode
from django.core.urlresolvers import reverse

from .utils import ChangeListUrlGetter, model_to_app_and_classname


class SearchShortcut(object):
    title = ''
    options = None
    filters = None
    request = None
    base_url_name = "search"

    def __init__(self, context):
        self.request = context['request']
        # Even is no filter is needed for a particular shorcut,
        # a formset always needs at least one form, so give by default one
        # empty form (which is allowed).
        self.filters = [{}]

    def get_title(self):
        return self.title

    def get_data(self):
        data = {}
        data.update(self.get_options_data())
        data.update(self.get_filters_data())

        # Add management_form data, according to number of forms in the formset
        data.update({
            'form-TOTAL_FORMS': len(self.filters),
            'form-INITIAL_FORMS': 0,
            'form-MAX_NUM_FORMS': '',
        })

        return data

    def get_filters_data(self):
        """
        Build filters's query string fragment.

        We need to add prefix form-0-, form-1, etc.,  to
        each field of each form of the formset.
        """
        filters_data = {}
        for i, filt in enumerate(self.filters):
            prefix = 'form-%s-' % (i,)
            for key, value in filt.items():
                filters_data.update({
                    prefix + key: value
                })

        return filters_data

    def get_options_data(self):
        """
        Build search options's query_string fragment.
        """
        return self.options

    @property
    def query_string(self):
        return urlencode(self.get_data())

    @property
    def base_url(self):
        return reverse(self.base_url_name)

    def get_url(self):
        return '%s?%s' % (self.base_url, self.query_string)


class AdminSearchShortcut(SearchShortcut):
    changelist_url_getter = ChangeListUrlGetter()

    def __init__(self, context):
        super(AdminSearchShortcut, self).__init__(context)
        self.admin_site_name = context.current_app

    @property
    def base_url(self):
        app_label, classname = model_to_app_and_classname(self.options['model'])
        return self.changelist_url_getter.get_url(self.admin_site_name, app_label, classname)
