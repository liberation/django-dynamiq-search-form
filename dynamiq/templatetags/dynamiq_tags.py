# -*- coding: utf-8 -*-
from django.utils import simplejson
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django import template

from dynamiq.utils import get_advanced_search_formset_class

register = template.Library()


def render_dynamiq_form(context, form_class):
    """
    A method to be used within an inclusion tag that render a search form.
    Should be called with a context and a search_form class inherited from
    DynamiqSearchForm.
    """
    # If we are already in a search results page (i.e. we have a change list),
    # load form from ChangeList instance in context, otherwise instantiate
    # a brand new one.
    cl = context.get('cl', None)
    if cl and hasattr(cl, 'search_form'):
        form = cl.search_form
    else:
        form = form_class(user=context['request'].user,
                          admin_site_name=context.current_app,
                          prefix=form_class.PREFIX)

    return {
        'search_form': form,
        'request': context['request'],
    }


def render_dynamiq_advanced_formset(context,
                                    formset_base_class,
                                    form_class):
    """
    A method to be used within an inclusion tag that render an advanced
    search formset.
    Should be called with a context and a search_form class inherited from
    DynamiqSearchForm.
    """
    # If we are already in a search results page (i.e. we have a change list),
    # load form from ChangeList instance in context, otherwise instantiate
    # a brand new one.
    formset = context.get('formset', context.get('form', None))
    if not formset:
        user = context['request'].user
        formset_class = get_advanced_search_formset_class(
                            user,
                            formset_base_class,
                            form_class
                        )
        formset = formset_class(user=user)

    return {
        'search_advanced_formset': formset,
        'request': context['request'],
        'js_filters_builders': [(label, simplejson.dumps(data)) for label, data in form_class.JS_FILTERS_BUILDERS]
    }


@register.filter
def render_dynamiq_label(label, autoescape=None):
    if autoescape:
        escape = conditional_escape
    else:
        escape = lambda x: x
    # formatted_label = u'<span class="label_classname">%s</span> vérifiant ' % escape(label[0])
    formatted_label = ""
    for l in label:
        if isinstance(l, dict):
            # Assemble query fragment, escaping all dict values first
            dict(zip(l.keys(), map(escape, l.values())))
            formatted_label += u"<span class=\"label_fragment\">" \
                               "<span class=\"label_name\">%(name)s</span> " \
                               "<span class=\"label_lookup\">%(lookup)s</span> " \
                               "<span class=\"label_value\">%(value)s</span>" \
                               "</span>" % l
        else:
            # if item is not a dict, then it's an AND/OR operator
            formatted_label += u' <span class="label_operator">%s</span> ' % (escape(l),)
    return mark_safe(formatted_label)
render_dynamiq_label.needs_autoescape = True
