from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser import edit
from plone.dexterity.browser import view
from plone import api as plone_api
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.browser.text import TextWidget


def icon_for_field(fieldname):
    """Helper method for translating from field names to
    prototype classes"""
    if '.' in fieldname:
        # Remove behaviour prefixes from fieldnames
        fieldname = fieldname.split('.')[-1]
    default = 'icon-right-open'
    mapping = {
        'email': 'icon-mail',
        'telephone': 'icon-phone',
        'mobile': 'icon-phone',
        'address': 'icon-home',
        'department': 'icon-building',
        'time_zone': 'icon-clock',
        'primary_location': 'icon-globe',
    }
    return mapping.get(fieldname, default)


def get_fields_for_template(form):
    """Helper method to get widget information for view/edit templates"""
    fields = []
    for field_name in form.widgets.keys():
        widget = form.widgets[field_name]
        if widget.error:
            error_html = widget.error.render()
        else:
            error_html = None

        fields.append({
            'name': field_name,
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
        """Look up hidden fields from registry"""
        hidden = plone_api.portal.get_registry_record(
            'ploneintranet.userprofile.hidden_fields')
        # Portrait is edited elsewhere
        hidden = hidden + ('portrait', )
        return hidden

    def _read_only_fields(self):
        """Look up read-only fields from registry"""
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
        """Mark read only fields as 'display'"""
        super(UserProfileBaseForm, self).updateWidgets()
        read_only_fields = self._read_only_fields()
        for fieldname, widget in self.widgets.items():
            if fieldname in read_only_fields:
                widget.mode = 'display'
            # Set up sizes correctly for prototype
            if isinstance(widget, TextWidget):
                if not widget.size:
                    widget.size = 50
            if isinstance(widget, TextAreaWidget):
                if not widget.rows:
                    widget.rows = 14


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
                         'person_title',
                         'first_name',
                         'last_name',
                         'IUserProfileAdditional.biography', )


class UserProfileEditView(edit.DefaultEditView):

    """Custom profile edit page that renders the edit form
    using prototype-compatible markup"""

    form = UserProfileEditForm
    index = ViewPageTemplateFile('templates/userprofile-edit.pt')

    def fields_for_edit(self):
        return get_fields_for_template(self.form_instance)
