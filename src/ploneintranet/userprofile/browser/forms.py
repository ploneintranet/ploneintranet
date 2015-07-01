from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser import edit
from plone.dexterity.browser import view
from plone import api as plone_api


def icon_for_field(fieldname):
    """Help method for translating from field names to
    prototype classes"""
    if '.' in fieldname:
        # Remove behaviour prefixes from fieldnames
        fieldname = fieldname.split('.')[-1]
    default = 'icon-right-open'
    mapping = {
        'email': 'icon-mail',
        'telephone': 'icon-phone',
        'mobile': 'icon-phone',
        'department': 'icon-building',
        'time_zone': 'icon-clock',
        'primary_location': 'icon-globe',
    }
    return mapping.get(fieldname, default)


def get_fields(form):
    """Helper method to get widget information for view/edit templates"""
    fields = []
    for field_name in form.widgets.keys():
        widget = form.widgets[field_name]
        if widget.error:
            error_html = widget.error.render()
        else:
            error_html = None

        fields.append({
            'label': widget.label,
            'description': widget.field.description,
            'read_only': widget.mode == 'display',
            'html': widget.render(),
            'error_html': error_html,
            'raw': widget.value,
            'icon_class': icon_for_field(field_name),
        })
    return fields


class UserProfileBaseForm(object):

    """Custom user profile form base allowing field visibility
    to be controlled via registry settings
    """

    def _hidden_fields(self):
        # Portrait is always hidden from this edit page
        hidden = plone_api.portal.get_registry_record(
            'ploneintranet.userprofile.hidden_fields')
        hidden = hidden + ('portrait', )
        return hidden

    def _read_only_fields(self):
        read_only = plone_api.portal.get_registry_record(
            'ploneintranet.userprofile.read_only_fields')
        return read_only

    def updateFieldsFromSchemata(self):
        """Remove hidden fields from the form"""
        super(UserProfileBaseForm, self).updateFieldsFromSchemata()
        hidden_fields = self._hidden_fields()
        for hidden_field in hidden_fields:
            self.fields = self.fields.omit(hidden_field)

    def updateWidgets(self):
        """Update widgets for read only fields"""
        super(UserProfileBaseForm, self).updateWidgets()
        read_only_fields = self._read_only_fields()
        for fieldname, widget in self.widgets.items():
            if fieldname in read_only_fields:
                widget.mode = 'display'


class UserProfileEditForm(UserProfileBaseForm, edit.DefaultEditForm):

    """Editable user profile form"""
    pass


class UserProfileViewForm(UserProfileBaseForm, view.DefaultView):

    """Non-editable user profile form"""

    def _hidden_fields(self):
        hidden = super(UserProfileViewForm, self)._hidden_fields()
        # Username, name and bio are dealt with differently
        # on the profile view page
        return hidden + ('username',
                         'first_name',
                         'last_name',
                         'IUserProfileAdditional.biography', )


class UserProfileEditView(edit.DefaultEditView):

    """Custom profile edit page that renders the edit form
    using prototype-compatible markup"""

    form = UserProfileEditForm
    index = ViewPageTemplateFile('templates/userprofile-edit.pt')

    def fields_for_edit(self):
        return get_fields(self.form_instance)
