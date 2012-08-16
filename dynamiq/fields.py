# -*- coding: utf-8 -*-
import time
import calendar

from datetime import date

from django import forms
from django.forms.fields import MultiValueField, DateField, IntegerField
from django.core.exceptions import ValidationError

from extended_choices import Choices
from extended_choices.fields import ExtendedChoiceField, ExtendedTypedChoiceField

from ajax_select.fields import AutoCompleteField

from .widgets import (BetweenDateWidget, MultiAutocompleteWidget,
                          IntegerSliderWithInput)


class DynamiqChoiceFieldMixin(ExtendedChoiceField):
    """
    An ExtendedChoiceField, with some values by default.
    The default widget, if not defined, is a forms.Select.
    The css_class argument is only for this default widget
    """

    def __init__(self, choices=None, required=False, widget=None, css_class='filter_value'):
        if widget is None:
            attrs = {}
            if css_class is not None:
                attrs = {'class': css_class}
            widget = forms.Select(attrs=attrs)

        params = dict(
            required=required,
            extended_choices=choices or Choices(),
            widget=widget
            )

        return super(DynamiqChoiceFieldMixin, self).__init__(**params)


class DynamiqChoiceField(DynamiqChoiceFieldMixin, ExtendedChoiceField):
    """
    ExtendedChoiceField that also uses DynamiqChoiceFieldMixin. In addition,
    if passed a value that looks like a list, return a list (splitting by ",")
    when cleaning it.
    """
    def clean(self, value):
        rval = super(DynamiqChoiceField, self).clean(value)
        if rval and "," in rval:
            rval = rval.split(',')

        return rval


class DynamiqIntChoiceField(DynamiqChoiceFieldMixin, ExtendedTypedChoiceField):
    def __init__(self, *args, **kwargs):
        super(DynamiqIntChoiceField, self).__init__(*args, **kwargs)
        self.coerce = int


class DynamiqStrChoiceField(DynamiqChoiceFieldMixin, ExtendedTypedChoiceField):
    def __init__(self, *args, **kwargs):
        super(DynamiqStrChoiceField, self).__init__(*args, **kwargs)
        self.coerce = str


class DynamiqBooleanChoiceField(DynamiqChoiceFieldMixin, ExtendedTypedChoiceField):

    def clean(self, value):
        # It expects an int based ExtendedChoices
        try:
            return int(value) == 1
        except TypeError:
            return False


class ExtraWidgetAttrsMixin(object):
    def __init__(self, *args, **kwargs):
        self.extra_widget_attrs = kwargs.pop('widgets_attrs', {})
        super(ExtraWidgetAttrsMixin, self).__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        return self.extra_widget_attrs


class CommaSeparatedChoiceField(ExtendedChoiceField):
    """
    ExtendedChoiceField that converts any valid choice into a list.
    """
    def clean(self, value):
        rval = super(CommaSeparatedChoiceField, self).clean(value)
        if rval:
            rval = rval.split(',')

        return rval


class DynamiqSearchAutoCompleteField(ExtraWidgetAttrsMixin, MultiValueField):
    channel = 'dynamiq_search'

    def __init__(self, *args, **kwargs):
        # We have one basic IntegerField (hidden) containing the id of the
        # author, and an AutocompleteField, which receives the dummy channel
        # to make ajax_selects happy.
        fields = (
            forms.CharField(),
            AutoCompleteField(self.channel),
        )
        # Pre-initialize widget, because it needs to receive the channel as well.
        # django only calls widget.__init__() if it's a class - if it's already
        # and instance it just skips that.
        self.widget = MultiAutocompleteWidget(self.channel)
        self.value_for_display = None
        super(DynamiqSearchAutoCompleteField, self).__init__(fields, *args, **kwargs)

    def get_value_display(self):
        return self.value_for_display

    def compress(self, data_list):
        # data_list[0] contains the id
        # data_list[1] contains the full name
        # We don't care about the full name when clean()ing, we just need the
        # id to give it to sesql.
        if data_list:
            self.value_for_display = data_list[1]
            return data_list[0]
        return None


class BetweenDateField(ExtraWidgetAttrsMixin, MultiValueField):
    widget = BetweenDateWidget

    def __init__(self, input_date_formats=None, localize=False, *args, **kwargs):
        fields = (
            DateField(input_formats=input_date_formats, localize=localize),
            DateField(input_formats=input_date_formats, localize=localize),
        )
        super(BetweenDateField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        # We simply return the data_list here, because sesql expects a list
        # with the 2 dates anyway, so there is no need for any kind of special
        # treatment here.
        # FIXME : maybe some validity check, like check if empty, since
        # MultiValueField automatically adds required=False to the internal
        # fields ?
        # FIXME : what really happens when we keep a list ? is the widget's
        # decompress() method called?
        return data_list


class DynamiqAdvancedChoiceField(ExtendedChoiceField):

    def set_widget_determination_options(self, filter_determination_methods, filter_type=None):
        self.widget.filter_type_determination = filter_determination_methods.get('filter_type')
        self.widget.filter_receptacle_determination = filter_determination_methods.get('filter_receptacle')
        self.widget.filter_autocomplete_lookup_determination = filter_determination_methods.get('filter_autocomplete_lookup')
        self.widget.filter_type = filter_type


class IntegerFieldWithSlider(IntegerField):
    """
    A simple integer field with a slider to select value.
    """
    def __init__(self, *args, **kwargs):
        super(IntegerFieldWithSlider, self).__init__(*args, **kwargs)
        self.widget = IntegerSliderWithInput(
                min_value=self.min_value,
                max_value=self.max_value,
            )


# This was introduced because of #636
class PolymorphicDateField(DateField):
    """Accepts ``%i/%m/%Y``, ``%m/%Y`` and ``%Y``. Cleanned data
    contains a tuple of the kind of date and a datetime object
    """

    # It could have been done globally by overriding
    # ``settings.DATETIME_INPUT_FORMATS`` but it not safe since its a global
    # setting. Plus, it wouldn't give us date intervals...

    def to_python(self, value):
        """
        Validates that the input can be converted to a date. If it fails
        we try to convert it to a year or month date and return a tuple
        with the kind of date and two date object that represent the period

        For 01/02/2012 the returned value is a date
        For 02/2012 the returned value ('month', date(2012, 02, 01), date(2012, 02, 29))
        For 2012 the returned value ('year', date(2012, 01, 01), date(2012, 12, 31))
        """
        try:
            value = super(PolymorphicDateField, self).to_python(value)
        except ValidationError:
            try:
                year = time.strptime(value, '%Y')[0]
                value = (date(year, 1, 1), date(year, 12, 31))
            except ValueError:
                try:
                    year, month = time.strptime(value, '%m/%Y')[:2]
                    last_day_of_month = calendar.monthrange(year, month)[1]
                    value = (date(year, month, 1), date(year, month, last_day_of_month))
                except ValueError:
                    raise ValidationError(self.error_messages['invalid'])
                else:
                    shortcut_kind = 'month'
            else:
                shortcut_kind = 'year'
            return (shortcut_kind, value)
        else:
            return value
