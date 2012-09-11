# -*- coding: utf-8 -*-

from django import forms
from django.forms.formsets import BaseFormSet

from extended_choices import Choices
from extended_choices.fields import ExtendedChoiceField


from dynamiq.fields import (DynamiqAdvancedChoiceField, DynamiqBooleanChoiceField,
                         DynamiqSearchAutoCompleteField, BetweenDateField,
                         DynamiqChoiceField, DynamiqIntChoiceField,
                         PolymorphicDateField)
from dynamiq.widgets import DynamiqAdvancedDynamicSelect
from .constants import (FILTER_LOOKUPS_STR, FILTER_LOOKUPS_INT,
                        FILTER_LOOKUPS_DATE, FILTER_LOOKUPS,
                        FILTER_RIGHT_OP, FILTER_DATE_RELATIVE,
                        LOOKUP_NEGATIVE_PREFIX, YES_NO, FILTER_LOOKUPS_ID,
                        FILTER_LOOKUPS_YES_NO, FILTER_LOOKUPS_ALIASES)


class DynamiqOptionsMixin(object):
    """
    Mixin which adds an instance of DynamiqOptionsForm in a .options_form
    property. To be used with a simple search form (see DynamiqSearchForm) or an
    advanced search formset (see DynamiqSearchAdvancedFormset), as they share same
    search options.

    If both simple and advanced search are used in the same page, give one of
    them a 'prefix' in order that the form options' fields don't get the same
    HTML id.

    Note that method is_valid() of main form / formset will check for
    options_form's validity as well. Notetheless, options_form's errors
    *will not* be displayed in the main form .errors at the moment.
    """
    def _options_form(self, initial=None, prefix=None):
        if self.is_bound:
            form = self.options_form_class(
                       self.data,
                       auto_id=self.auto_id,
                       prefix=prefix,
                       main_form=self
                   )
        else:
            form = self.options_form_class(
                       auto_id=self.auto_id,
                       prefix=prefix,
                       initial=self.initial_options,
                       main_form=self
                   )

        return form

    def __init__(self, data=None, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.default_model = kwargs.pop('default_model', None)
        self.initial_options = None
        if data is None:
            # If no data is passed, i.e. form is not bound, force initial
            # data according to user's group
            # FIXME add test for that!
            kwargs['initial'], self.initial_options = self.get_initial_data()
        super(DynamiqOptionsMixin, self).__init__(data, *args, **kwargs)
        prefix = kwargs.get('prefix', None)
        self.options_form = self._options_form(prefix=prefix)
        if self.is_bound and data is None:
            # See WARNING above
            raise('data should always be passed as a kwargs!')

    def get_initial_data(self):
        """
        Set .initial for .options_form and return .initial for main form.
        Override me.
        """
        initial = {}
        initial_options = {}
        return initial, initial_options

    def is_valid(self):
        return self.options_form.is_valid() and super(DynamiqOptionsMixin, self).is_valid()


class DynamiqSearchOptionsForm(forms.Form):

    limit = forms.IntegerField(
                min_value=1,
                max_value=100,
                required=True,
                initial=15,
                label=u"Nombre de résultats"
            )
    sort = DynamiqChoiceField(
               choices=Choices(),
               required=False,
               label=u"Trier par",
               css_class="sort"
           )

    def __init__(self, *args, **kwargs):
        self.main_form = kwargs.pop('main_form')
        self.user = self.main_form.user

        super(DynamiqSearchOptionsForm, self).__init__(*args, **kwargs)

        self.fields['sort'].extended_choices = self.SORT
        self.fields['sort'].initial = self.SORT_INITIAL


class DynamiqAdvancedFormset(DynamiqOptionsMixin, BaseFormSet):

    @property
    def FILTER_NAME(self):
        return self.empty_form.FILTER_NAME


class DynamiqAdvancedForm(forms.Form):
    error_css_class = 'errors'

    # Lookup filters
    FILTER_LOOKUPS_FULLTEXT = ()  # Defined by SeSQL or Haystack
    FILTER_LOOKUPS_STR = FILTER_LOOKUPS_STR
    FILTER_LOOKUPS_INT = FILTER_LOOKUPS_INT
    FILTER_LOOKUPS_ID = FILTER_LOOKUPS_ID
    FILTER_LOOKUPS_YES_NO = FILTER_LOOKUPS_YES_NO
    FILTER_LOOKUPS_DATE = FILTER_LOOKUPS_DATE
    FILTER_LOOKUPS = FILTER_LOOKUPS
    FILTER_RIGHT_OP = FILTER_RIGHT_OP
    FILTER_DATE_RELATIVE = FILTER_DATE_RELATIVE
    LOOKUP_NEGATIVE_PREFIX = LOOKUP_NEGATIVE_PREFIX
    FILTER_LOOKUPS_ALIASES = FILTER_LOOKUPS_ALIASES

    FILTER_NAME = Choices(
        ('FULLTEXT', 'fulltext', u'Tout'),
    )
    DEFAULT_FILTER_NAME = FILTER_NAME.FULLTEXT
    FILTERS_NAMES_BY_GROUP = {
        # 'group_name': FILTER_NAME.FOR_somegroup (subset)
    }

    YES_NO = YES_NO

    # placeholder for fields mapping
    _FILTERS_BY_FIELD = {
        # 'field_name': {
        #     'type': 'field_type',
        #     'receptacle': 'field_receptacle',
        # },
    }

    # List of filters "builders": list of (label, {filter params}) used to dynamically
    # build advanced filters with JS
    #
    # -- SYNTAX
    #
    # (u'label', {
    #     'filter_name': ..., # Required: specify which filter_name to select in build filter
    #     'filter_lookup': ..., # Optional: use it to you don't want default lookup for specified filter_name
    #     'filter_value': ..., # Optional: use it to specify a particular value
    #     'right_op': ..., # Optional
    #     'previous_right_op': ..., # Optional
    #     'replace': True  # Optional: means build filter will replace all existing ones
    # })
    #
    JS_FILTERS_BUILDERS = (
        (u'vider', {
            'replace': True,
            'filter_name': 'fulltext'
        }),
    )

    # filter name field
    filter_name = DynamiqAdvancedChoiceField(
        extended_choices=FILTER_NAME,
        widget=DynamiqAdvancedDynamicSelect(attrs={'class': 'filter_name'})
    )

    # Form lookup fields
    fulltext_lookup = ExtendedChoiceField(
        required=False,
        extended_choices=FILTER_LOOKUPS_FULLTEXT,
        widget=forms.Select(attrs={'class': 'filter_lookup'})
    )
    str_lookup = ExtendedChoiceField(
        required=False,
        extended_choices=FILTER_LOOKUPS_STR,
        widget=forms.Select(attrs={'class': 'filter_lookup'})
    )
    int_lookup = ExtendedChoiceField(
        required=False,
        extended_choices=FILTER_LOOKUPS_INT,
        widget=forms.Select(attrs={'class': 'filter_lookup'})
    )
    id_lookup = ExtendedChoiceField(
        required=False,
        extended_choices=FILTER_LOOKUPS_ID,
        widget=forms.Select(attrs={'class': 'filter_lookup'})
    )
    yes_no_lookup = ExtendedChoiceField(
        required=False,
        extended_choices=FILTER_LOOKUPS_YES_NO,
        widget=forms.Select(attrs={'class': 'filter_lookup'})
    )
    date_lookup = DynamiqAdvancedChoiceField(
        required=False,
        extended_choices=FILTER_LOOKUPS_DATE,
        widget=DynamiqAdvancedDynamicSelect(attrs={'class': 'filter_lookup'})
    )

    # Value receptacle fields
    filter_value_fulltext = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'filter_value'}))
    filter_value_str = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'filter_value'}))
    filter_value_date = PolymorphicDateField(required=False, widget=forms.DateInput(attrs={'class': 'filter_value'}))
    filter_value_date_between = BetweenDateField(required=False, widgets_attrs={'class': 'filter_value filter_value_multiple'})
    filter_value_date_relative = DynamiqIntChoiceField(FILTER_DATE_RELATIVE)
    filter_value_int = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'filter_value'}))
    filter_value_id = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'filter_value'}))
    filter_value_autocomplete = DynamiqSearchAutoCompleteField(required=False, widgets_attrs={'class': 'filter_value autocompleted'})
    filter_value_yes_no = DynamiqBooleanChoiceField(YES_NO)

    # AND / OR
    filter_right_op = DynamiqChoiceField(FILTER_RIGHT_OP, css_class='right_op')

    # These following 2 fields are only used to hold finale lookup and value
    # in the clean() method. Don't touch them outside clean(), and
    # never display them !
    filter_lookup = forms.CharField(required=False, widget=forms.HiddenInput)
    filter_value = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(DynamiqAdvancedForm, self).__init__(*args, **kwargs)

        # Choices of field .filter_name depends on user's group.
        # Build the choices dynamically and alter the field accordingly.
        # TODO : check extended_choices / choices
        self.fields['filter_name'].extended_choices = self.FILTER_NAME
        self.fields['filter_name'].choices = self._build_filter_name_choices()

        # Then, set our callbacks that help the widgets display/hide other fields
        filter_determination_methods = {
            'filter_type': self.determine_filter_type,
            'filter_receptacle': self.determine_filter_receptacle,
            'filter_autocomplete_lookup': self.determine_filter_autocomplete_lookup,
        }
        self.fields['filter_name'].set_widget_determination_options(filter_determination_methods)
        self.fields['date_lookup'].set_widget_determination_options(filter_determination_methods, filter_type="date")

        # self.fields is a SortedDict, and we WANT `filter_right_op` to always
        # the last field for display consistency
        self.fields['filter_right_op'] = self.fields.pop('filter_right_op')

    def _build_filter_name_choices(self):
        """Build filter_name.choices. Override to define specifics choices per user."""
        return self.FILTER_NAME.CHOICES

    @classmethod
    def determine_filter_autocomplete_lookup(cls, filter_name):
        return cls._FILTERS_BY_FIELD.get(filter_name, {}).get('autocomplete_lookup')

    @classmethod
    def determine_filter_receptacle(cls, filter_name, filter_type=None, filter_lookup=None):
        """
        Return the receptacle to use depending on the name and lookup
        chosen.

        For instance, if the user selects "Date de publication" and then
        the "relative" value for date_lookup, we need to display the
        use the receptacle "filter_value_date".
        """
        # Simple cases can be expressed simply using the reverted dict statically
        # built in the form. Complex cases that depend on both the name and the
        # lookup value can not, and we need specific if/else cases.
        if filter_type == 'date' and filter_lookup == cls.FILTER_LOOKUPS_DATE.RELATIVE:
            receptacle_name = 'date_relative'
        elif filter_type == 'date' and filter_lookup == cls.FILTER_LOOKUPS_DATE.BETWEEN:
            receptacle_name = 'date_between'
        elif filter_type == 'date':
            receptacle_name = 'date'
        else:
            receptacle_name = cls._FILTERS_BY_FIELD.get(filter_name, {}).get('receptacle')
        return receptacle_name

    @classmethod
    def determine_filter_type(cls, name):
        """
        Return the "type" corresponding to a specific filter name.
        """
        return cls._FILTERS_BY_FIELD.get(name, {}).get('type')

    @classmethod
    def determine_filter_lookup_for_alias(cls, alias, ftype=None):
        """
        Return the original lookup name for an alias.
        For example "!=" will return "not_contains" with default settings.
        """
        if (ftype
            and ftype in cls.FILTER_LOOKUPS_ALIASES
            and alias in cls.FILTER_LOOKUPS_ALIASES[ftype]):
            lookup = cls.FILTER_LOOKUPS_ALIASES[ftype][alias]
        elif alias in cls.FILTER_LOOKUPS_ALIASES:
            lookup = cls.FILTER_LOOKUPS_ALIASES[alias]
        else:
            lookup = alias
        return lookup

    def clean(self):
        """
        Remove unused fields and keep only filter's final data.

        Filter's final data means:
        * a name: editorial_source, workflow_state, title, etc.
        * a lookup: containswords, exact, gte, etc.
        * a value
        * a right_op: how is the filter connected with the next
            one (with an "AND" operator ? With an "OR" operator ?) ? Or is
            it the last one ?

        Use dedicated (sometimes hidden) fields to hold this final
        data, which be later used in changelist.

        "Final" fields are:
        * filter_name
        * filter_lookup
        * filter_value
        * filter_right_op
        """
        if bool(self.errors):
            # Don't bother validating the form unless each field is valid on its own
            return

        cleaned_data = self.cleaned_data
        filter_name = cleaned_data.get('filter_name')
        filter_type = self.determine_filter_type(filter_name)
        filter_lookup = cleaned_data.get(filter_type + '_lookup')
        filter_value_receptacle = self.determine_filter_receptacle(filter_name, filter_type, filter_lookup)
        filter_value = cleaned_data.get('filter_value_' + filter_value_receptacle)

        if not (filter_name and filter_lookup):
            raise forms.ValidationError('Il manque des données pour ce critère !')

        # Overwrite cleaned_data to leave only "final" fields for later use
        cleaned_data = {
            'filter_name': filter_name,
            'filter_lookup': filter_lookup,
            'filter_value': filter_value,  # Tricky part: filter_value is a CharField, but we don't care anymore at this point, we put final data whatever type it is.
            'filter_right_op': cleaned_data['filter_right_op'],
        }

        return cleaned_data
