# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.forms.widgets import MultiWidget, DateInput
from django.utils.html import escape, conditional_escape
from django.utils.text import force_unicode
from django.utils.formats import get_format

from ajax_select.fields import AutoCompleteWidget

from .utils import model_to_app_and_classname


class AdvancedDynamicSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super(AdvancedDynamicSelect, self).__init__(*args, **kwargs)
        self.filter_type = None

    def build_attrs(self, attrs=None, **kwargs):
        rval = super(AdvancedDynamicSelect, self).build_attrs(attrs, **kwargs)
        if 'class' in rval:
            rval['class'] += ' dynamic_select'
        else:
            rval['class'] = 'dynamic_select'
        return rval

    def render_option(self, selected_choices, option_value, option_label):
        # Note: the various self.filter_* methods are dynamically added to the
        # widget by the field.
        option_value = force_unicode(option_value)
        selected_html = (option_value in selected_choices) and u' selected="selected"' or ''

        data_lookup = self.filter_type_determination(option_value)
        data_filter_value = self.filter_receptacle_determination(option_value, filter_type=self.filter_type, filter_lookup=option_value)
        data_autocomplete_lookup = self.filter_autocomplete_lookup_determination(option_value)

        data_lookup = data_lookup and ' data-filtertype="%s"' % (data_lookup, ) or ""
        data_filter_value = data_filter_value and ' data-filtervalue="%s"' % (data_filter_value, ) or ""
        data_autocomplete_lookup = data_autocomplete_lookup and ' data-filterautocomplete="%s"' % (reverse('ajax_lookup', kwargs={'channel': data_autocomplete_lookup}), ) or ""

        return u'<option value="%s"%s%s%s%s>%s</option>' % (
            escape(option_value), selected_html,
            data_lookup, data_filter_value, data_autocomplete_lookup,
            conditional_escape(force_unicode(option_label)))


class BetweenDateWidget(MultiWidget):
    date_format = None

    def __init__(self, attrs=None, date_format=None):
        if not date_format:
            date_format = get_format('DATE_INPUT_FORMATS')[0]
        widgets = (DateInput(attrs=attrs, format=date_format),
                   DateInput(attrs=attrs, format=date_format))
        super(BetweenDateWidget, self).__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        return u'<span class="filter_value filter_value_combine">et</span>'.join(rendered_widgets)

    def decompress(self, value):
        if value:
            return [value[0].date(), value[1].date()]
        return [None, None]


class MultiAutocompleteWidget(MultiWidget):
    def __init__(self, channel, attrs=None):
        # First widget is an hidden input containing the "id"
        # Second widget is the actual autocomplete widget, displaying the "name"
        # (it will also fill-in *both* widgets when autocompleting)
        widgets = (forms.HiddenInput(attrs=attrs),
                   AutoCompleteWidget(channel, attrs=attrs))

        super(MultiAutocompleteWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value[0]
        return [None, None]


class ModelSelect(forms.Select):
    """
    Render a Model select that take care of the changelist URL.
    """

    def __init__(self, *args, **kwargs):
        self.admin_site_name = kwargs.pop('admin_site_name')
        self.changelist_url_getter = kwargs.pop('changelist_url_getter')
        super(ModelSelect, self).__init__(*args, **kwargs)

    def build_attrs(self, attrs=None, **kwargs):
        rval = super(ModelSelect, self).build_attrs(attrs, **kwargs)
        rval.update({'class': 'js-change_model'})
        return rval

    def _render_option_parts(self, selected_choices, option_value, option_label):

        option_value = force_unicode(option_value)
        app_label, classname = model_to_app_and_classname(option_value)

        attributes = {
            'data-actionurl': self.changelist_url_getter.get_url(self.admin_site_name, app_label, classname)
        }
        if option_value in selected_choices:
            attributes['selected'] = 'selected'

        return {
            'value': escape(option_value),
            'attributes': attributes,
            'label': conditional_escape(force_unicode(option_label))
        }

    def render_option(self, selected_choices, option_value, option_label):
        parts = self._render_option_parts(selected_choices, option_value, option_label)
        attr_str = ' '.join([u'%s="%s"' % (key, value) for key, value in parts['attributes'].iteritems()])
        return u'<option value="%s"%s>%s</option>' % (parts['value'], attr_str, parts['label'])


class AdvancedModelSelect(ModelSelect):
    """
    In advanced search mode, active/unactive filters according to the model
    selection.
    """

    def __init__(self, *args, **kwargs):
        self.options_form = kwargs.pop('options_form', None)
        super(AdvancedModelSelect, self).__init__(*args, **kwargs)

    def _render_option_parts(self, selected_choices, option_value, option_label):
        parts = super(AdvancedModelSelect, self)._render_option_parts(selected_choices, option_value, option_label)

        if hasattr(self, 'options_form') and hasattr(self.options_form, 'MODEL_OPTIONS') \
            and hasattr(self.options_form, 'main_form'):

            sort_options = []
            for option in self.options_form.MODEL_OPTIONS[option_value]['sort']:
                sort_options.append(getattr(self.options_form.SORT, option))
            parts['attributes']['data-sort'] = '|'.join(sort_options)

            if hasattr(self.options_form.main_form, 'FILTER_NAME'):
                filters = []
                for filtr in self.options_form.MODEL_OPTIONS[option_value]['filters']:
                    filters.append(getattr(self.options_form.main_form.FILTER_NAME, filtr))
                parts['attributes']['data-filters'] = '|'.join(filters)

        return parts
