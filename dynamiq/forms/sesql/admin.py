# -*- coding: utf-8 -*-

from dynamiq.forms.base import SearchOptionsMixin
from dynamiq.utils import ChangeListUrlGetter
from dynamiq.widgets import AdvancedModelSelect
from . import SeSQLOptionsForm


class SeSQLAdminSearchOptionsMixin(SearchOptionsMixin):
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

        # Use a widget to manage the admin changelist URL
        self.fields['model'].widget = AdvancedModelSelect(
                choices=self._build_models_choices(),
                admin_site_name=self.admin_site_name,
                changelist_url_getter=self.changelist_url_getter,
                options_form=self
            )

    def _build_models_choices(self):
        """Build model.choices at runtime. Override me."""
        return self.MODEL.CHOICES
