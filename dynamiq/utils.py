# -*- coding: utf-8 -*-

import re

from datetime import date, timedelta

from django.utils.dateformat import DateFormat
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.utils.functional import curry
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError


def get_advanced_search_formset_class(user, formset_base_class, form_class):
    """
    Util to generate advanced search's formset with extra params and hacky
    currying in one single place.

    formet_class.form is curried in order to pass kwargs `user` to each
    individual form of the formset.

    From http://stackoverflow.com/questions/622982/django-passing-custom-form-parameters-to-formset/624013#624013.
    """
    formset_class = formset_factory(
                        form_class,
                        formset=formset_base_class,
                        extra=1
                    )
    formset_class.form = staticmethod(curry(form_class, user=user))

    return formset_class


class LabelOperator(unicode):
    pass


class LabelFragment(dict):
    pass


class LabelModel(unicode):
    pass


class BaseQBuilder(object):
    """
    Util that generates a Q query (set of Q objects connected to each others
    either by an OR or an AND operator) from an advanced search formset.
    """

    def stack_to_Q(self, stack):
        filters = None
        label = []
        for j, substack in enumerate(stack):
            tmp_label = []
            query_fragment = None
            for i, fragment in enumerate(substack):
                if i == 0:
                    query_fragment = fragment
                    tmp_label.append(fragment.label)
                else:
                    query_fragment &= fragment
                    tmp_label.append(LabelOperator(_('AND')))
                    tmp_label.append(fragment.label)
            if query_fragment:
                # Substack was empty (certainly an empty field)
                if j == 0:
                    filters = query_fragment
                    label.extend(tmp_label)
                else:
                    filters |= query_fragment
                    label.append(LabelOperator(_('OR')))
                    label.extend(tmp_label)

        return filters, label

    def generate_filter_with_label(self,
                                   form,
                                   filter_name,
                                   filter_lookup,
                                   filter_value):
        """
        Translate cleaned data from *one* form of advanced formset
        into a Q object. In addition, add a custom "label" attribute
        to that Q object to describe the query fragment.

        At this point, `filter_lookup` has already been validated
        against sesql accepted lookups, except that it can still be
        special lookups which need further treatment:
        * It can starts with LOOKUP_NEGATIVE_PREFIX ("not_"): it
            then has to be translated into a negated Q.
        * It can be EXACT: it has to be translated into "=".
        * It can be BETWEEN: it means that `filter_value` contains
        two date values that have to be translated into two Q
        objects with '__gte' and '__lte' lookups.
        * It can be RELATIVE: it means that `filter_value` contains
        an integer that has to be translated into a period with
        two dates.

        A special case must be handled for `filter_name` too:
        * it can be multi-valued: if it contains a ",",
        eg. "suptitle,title,subtitle", it means we have to split it
        into several OR-ed Q objects: Q("suptitle" ...) OR Q("title" ...) OR Q("subtitle" ...).
        """

        query_filter = None
        is_negated = False

        # Init label with default stuff, can be overidden later
        # Needs to be done before negation is transformed since we want the
        # french label for the lookup used without having to manually add
        # the negation later...
        filter_type = form.determine_filter_type(filter_name)
        label = LabelFragment({
            'name': form.FILTER_NAME.CHOICES_DICT[filter_name],
            'lookup': form.FILTER_LOOKUPS[filter_type].CHOICES_DICT.get(filter_lookup, ""),
            'value': filter_value,
        })
        filter_value_receptacle = form.determine_filter_receptacle(filter_name, filter_type, filter_lookup)
        filter_value_field = form.fields.get('filter_value_' + filter_value_receptacle, None)

        if filter_type == 'date' and isinstance(label['value'], date):
            label['value'] = DateFormat(label['value']).format(settings.DATE_FORMAT)
        elif hasattr(filter_value_field, 'get_value_display'):
            label['value'] = filter_value_field.get_value_display() or label['value']

        if filter_lookup.startswith(form.LOOKUP_NEGATIVE_PREFIX):
            is_negated = True
            filter_lookup = filter_lookup[len(form.LOOKUP_NEGATIVE_PREFIX):]

        if ',' in filter_name:
            # At this point, `filter_name` holds "several" filter_name,
            # we then need to split it into sub-filters, keeping
            # *same lookup and value*.
            # Used essentially for filter_name "titraille" (which is
            # in fact 'title,suptitle,subtitle').
            # Note: splitting filter_name into a list can't be
            # done into clean_filter_name() method: having a list
            # in cleaned_data breaks later on.
            subfilters = filter_name.split(',')
            for i, subfilter_name in enumerate(subfilters):
                if i == 0:
                    query_filter = self.generate_filter_with_label(
                        form,
                        subfilter_name,
                        filter_lookup,
                        filter_value
                    )
                else:
                    query_filter |= self.generate_filter_with_label(
                        form,
                        subfilter_name,
                        filter_lookup,
                        filter_value
                    )

        if filter_lookup == form.FILTER_LOOKUPS_DATE.BETWEEN:
            # At this point, filter_value is a list of two date
            # values, we have to split them into two Q objects
            Q1 = self.generate_filter_with_label(
                form,
                filter_name,
                form.FILTER_LOOKUPS_DATE.GTE,
                filter_value[0]
            )
            Q2 = self.generate_filter_with_label(
                form,
                filter_name,
                form.FILTER_LOOKUPS_DATE.LTE,
                filter_value[1]
            )
            query_filter = Q1 & Q2

            # Alter the label value to display the 2 dates in it
            label['value'] = ' et '.join([
                DateFormat(filter_value[0]).format(settings.DATE_FORMAT),
                DateFormat(filter_value[1]).format(settings.DATE_FORMAT),
            ])

        elif filter_lookup == form.FILTER_LOOKUPS_DATE.RELATIVE:
            # At this point, filter_value is an integer, which
            # is the number of days we want to search back on
            # the `filter_name` field.
            date1 = date.today()
            date2 = date1 - timedelta(days=filter_value)
            if date2 <= date1:
                from_date = date2
                to_date = date1
                from_lookup = form.FILTER_LOOKUPS_DATE.GTE
            else:
                # We are looking for a date in the future,
                # switch dates and exclude today from the search.
                # This is done essentially to exclude today's
                # production in search's shortcut "newspapers'
                # articles of tomorrow".
                from_date = date1
                to_date = date2
                from_lookup = 'gt'  # FIXME hard-coded!
            Q1 = self.generate_filter_with_label(
                form,
                filter_name,
                from_lookup,
                from_date
            )
            Q2 = self.generate_filter_with_label(
                form,
                filter_name,
                form.FILTER_LOOKUPS_DATE.LTE,
                to_date
            )
            query_filter = Q1 & Q2

            # For relative lookups, the label value is one of the
            # RELATIVE choices
            label['value'] = form.FILTER_DATE_RELATIVE.CHOICES_DICT[filter_value]

        elif filter_lookup == form.FILTER_LOOKUPS_INT.EXACT:
            if filter_type == 'date' and isinstance(filter_value, tuple):
                # At this point filter_value is a tuple which define a period
                # convert tuple to period
                kind = filter_value[0]
                start, end = filter_value[1]
                if kind == 'month':
                    label['value'] = start.strftime('%m-%Y')
                else:
                    label['value'] = start.strftime('%Y')
                Q1 = self.generate_filter_with_label(
                    form,
                    filter_name,
                    form.FILTER_LOOKUPS_DATE.GTE,
                    start
                )
                Q2 = self.generate_filter_with_label(
                    form,
                    filter_name,
                    form.FILTER_LOOKUPS_DATE.LTE,
                    end
                )
                query_filter = Q1 & Q2
            elif isinstance(filter_value, (list, tuple)):
                final_lookup = '%s__in' % (filter_name, )
            else:
                # FIXME ask SeSQL developers to implement 'exact' lookup!
                final_lookup = filter_name
        else:
            final_lookup = '%s__%s' % (filter_name, filter_lookup)

        if query_filter is None:
            # Q does not accept unicode keyword in python 2.6.1
            # TODO upgrade to 2.6.6 and break some Mac OS X !
            final_lookup = str(final_lookup)
            query_filter = Q(**{final_lookup: filter_value})

        if is_negated:
            query_filter = ~query_filter

        query_filter.label = label
        query_filter.is_negated = is_negated

        return query_filter


class FormsetQBuilder(BaseQBuilder):

    def __init__(self, formset):
        self.formset = formset

    def __call__(self):
        stack = []  # List of OR-ed filters groups
        current_stack = []  # Single group of AND-ed filters, inside stack
        stack.append(current_stack)
        for i, form in enumerate(self.formset.forms):
            cleaned_data = form.cleaned_data
            filter_name = cleaned_data.get('filter_name')
            filter_lookup = cleaned_data.get('filter_lookup')
            filter_value = cleaned_data.get('filter_value')
            filter_right_op = cleaned_data.get('filter_right_op')
            if filter_value == '' or filter_value is None:
                # Skip empty fields
                # Notice that doing so we can generate a stack with an
                # empty substack
                continue
            query_fragment = self.generate_filter_with_label(
                form, filter_name,
                filter_lookup,
                filter_value
            )

            current_stack.append(query_fragment)
            if filter_right_op == 'OR':
                # Since we found an OR operator, create new group to
                # hold following AND-ed filters
                current_stack = []
                stack.append(current_stack)

        return self.stack_to_Q(stack)


class ParsedStringQBuilder(BaseQBuilder):

    def __init__(self, q, form_class, raise_on_error=False):
        """
        `q` is the string to parse
        `form_class`, the AdvancedForm to use
        `raise_on_error` define if we raise a ValidationError if some form
        is not valid.
        """
        self.q = q
        self.form_class = form_class
        self.raise_on_error = raise_on_error

    def __call__(self):
        stack = []  # List of OR-ed filters groups
        current_stack = []  # Single group of AND-ed filters, inside stack
        stack.append(current_stack)
        query_elements = self.split_query_string(self.q)
        for i, el in enumerate(query_elements):
            els = self.split_query_element(el)
            filter_value = els[2] if len(els) == 3 else els[0]
            if not filter_value:
                # Skip empty fields
                # Notice that doing so we can generate a stack with an
                # empty substack
                continue
            if filter_value == 'OR':
                # Since we found an OR operator, create new group to
                # hold following AND-ed filters
                current_stack = []
                stack.append(current_stack)
                continue
            if filter_value == "AND":
                continue   # filters are AND-ed by default
            filter_name = els[0] if len(els) == 3 else self.form_class.DEFAULT_FILTER_NAME
            filter_lookup = els[1] if len(els) == 3 else "="
            filter_type = self.form_class.determine_filter_type(filter_name)
            if filter_value.startswith('-'):
                filter_value = filter_value[1:]
                if not filter_lookup.startswith('!'):
                    filter_lookup = "!%s" % filter_lookup
            filter_value = filter_value.strip('"+')  # TODO: manage exact
            filter_lookup = self.form_class.determine_filter_lookup_for_alias(filter_lookup, filter_type)
            filter_value_receptacle = self.form_class.determine_filter_receptacle(filter_name, filter_type, filter_lookup)
            form = self.form_class({
                "filter_name": filter_name,
                "%s_lookup" % filter_type: filter_lookup,
                'filter_value_%s' % filter_value_receptacle: filter_value,
            })
            if not form.is_valid():
                if self.raise_on_error:
                    raise ValidationError(form.errors)
                else:
                    # By default, the search query is displayed to user
                    # in a readable mode ("x contains y and z contains w")
                    # so not raising if some field is invalid seems an
                    # acceptable behaviour
                    continue
            query_fragment = self.generate_filter_with_label(
                form,
                filter_name,
                filter_lookup,
                filter_value
            )
            current_stack.append(query_fragment)

        return self.stack_to_Q(stack)

    @classmethod
    def split_query_string(cls, q):
        """
        Split on space unless they are in quotes.
        """
        pattern = re.compile(ur"""(?:[^ "]|"[^"]*")+""", re.U | re.X)
        return pattern.findall(q)

    @classmethod
    def split_query_element(cls, s):
        """
        Split one query string element in ['field_name', 'operator', 'value'].
        field:value => ['field', ':', 'value']
        """
        pattern = re.compile(ur"""
            [<=>\:\!]{1,2}(?#Separator)
            |[\w’\u2019 '"\-/]+(?#All others "words")
            """, re.U | re.X)
        return pattern.findall(s)


class ChangeListUrlGetter(object):
    """
    This object return the url for the changelist of a specific model, given as
    `classname`.
    The method to be called is `get_url`, the `normalize_classname` is only here
    for subclassing in case of specific needs
    """
    def normalize_classname(self, classname):
        return classname.lower()

    def get_url(self, admin_site_name, app_label, classname):
        classname = self.normalize_classname(classname)
        return reverse('admin:%s_%s_changelist' % (app_label, classname), current_app=admin_site_name)


def model_choice_value(model):
    """
    In MODEL_CHOICES, we need to add the app_label AND the model name
    """
    return '%s:%s' % (model._meta.app_label, model._meta.object_name)


def model_to_app_and_classname(choice):
    """
    It's the reverse of model_choice_value, to get the app_label and the
    model name (i.e. the classname to be sent to search engine).
    """
    if not choice:
        return (None, None)
    if isinstance(choice, basestring):
        classes = choice.split(',')
    else:
        classes = choice
    app_label = classes[0].split(':')[0]
    classname = ','.join([c.split(':')[1] for c in classes])
    return app_label, classname
