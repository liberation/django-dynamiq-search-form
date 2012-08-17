# -*- coding: utf-8 -*-
from django.utils import simplejson
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django import template

from dynamiq.utils import LabelModel

register = template.Library()


# ############ #
#     Tags     #
# ############ #

@register.inclusion_tag('dynamiq/simple_form.html')
def render_dynamiq_form(request, form):
    """
    Render a form.
    """
    return {
        'search_form': form,
        'request': request
    }


@register.inclusion_tag('dynamiq/advanced_formset.html')
def render_dynamiq_advanced_formset(request, formset):
    """
    Render a formset.
    """
    return {
        'search_advanced_formset': formset,
        'request': request,
        'js_filters_builders': [(label, simplejson.dumps(data)) for label, data in formset.form().JS_FILTERS_BUILDERS]
    }


# ############ #
#   Filters    #
# ############ #

@register.filter
def format_dynamiq_label(label, autoescape=None):
    if autoescape:
        escape = conditional_escape
    else:
        escape = lambda x: x
    if label and isinstance(label[0], LabelModel):
        # We have here a model label
        formatted_label = u'<span class="label_classname">%s</span> vérifiant ' % escape(label[0])
    else:
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
        elif isinstance(l, LabelModel):
            # LabelModel are printed at the beginning
            continue
        else:
            # if item is not a dict, then it's an AND/OR operator
            formatted_label += u' <span class="label_operator">%s</span> ' % (escape(l),)
    return mark_safe(formatted_label)
format_dynamiq_label.needs_autoescape = True
