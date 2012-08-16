# -*- coding: utf-8 -*-

from dynamiq.forms.base import DynamiqOptionsMixin
from dynamiq.utils import ChangeListUrlGetter
from dynamiq.widgets import DynamiqModelSelect
from . import SeSQLOptionsForm


class SeSQLAdminSearchOptionsMixin(DynamiqOptionsMixin):
    """
    Options mixin admin_site aware.
    """

    def __init__(self, data=None, *args, **kwargs):
        self.admin_site_name = kwargs.pop('admin_site_name', None)
        super(SeSQLAdminSearchOptionsMixin, self).__init__(data, *args, **kwargs)


class SeSQLAdminOptionsForm(SeSQLOptionsForm):
    changelist_url_getter = ChangeListUrlGetter()

    def __init__(self, *args, **kwargs):
        super(SeSQLAdminOptionsForm, self).__init__(*args, **kwargs)

        self.admin_site_name = self.main_form.admin_site_name

        self.fields['model'].extended_choices = self.MODEL
        self.fields['model'].initial = self.MODEL_INITIAL
        self.fields['model'].widget = DynamiqModelSelect(
                choices=self._build_models_choices(),
                admin_site_name=self.admin_site_name,
                changelist_url_getter=self.changelist_url_getter
            )

    def _build_models_choices(self):
        """Build model.choices at runtime. Override me."""
        return self.MODEL.CHOICES
