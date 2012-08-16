# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse
from django.contrib.admin import widgets
from django.forms.widgets import MultiWidget, DateInput
from django.utils.html import escape, conditional_escape
from django.utils.text import force_unicode
from django.utils.formats import get_format

from ajax_select.fields import AutoCompleteWidget


class DynamiqAdvancedDynamicSelect(forms.Select):
    def __init__(self, *args, **kwargs):
        super(DynamiqAdvancedDynamicSelect, self).__init__(*args, **kwargs)
        self.filter_type = None

    def build_attrs(self, attrs=None, **kwargs):
        rval = super(DynamiqAdvancedDynamicSelect, self).build_attrs(attrs, **kwargs)
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


class IntegerSliderWithInput(widgets.AdminIntegerFieldWidget):
    """
    A simple input for integer, with some data attributes and a specific
    class, to intercept it in JS and add a slider.
    """
    def __init__(self, min_value, max_value, steps=10, attrs=None):
        final_attrs = {
            'data-min': min_value,
            'data-max': max_value,
            'data-steps': steps,
            'class': 'vIntegerField js-integer-slider',
        }
        if attrs is not None:
            final_attrs.update(attrs)
        super(IntegerSliderWithInput, self).__init__(attrs=final_attrs)
