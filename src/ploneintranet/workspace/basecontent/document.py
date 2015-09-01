from Acquisition import aq_inner
from Products.Archetypes.utils import shasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser import add, edit
from z3c.form import button
from z3c.form.interfaces import IAddForm

from ploneintranet.core import ploneintranetCoreMessageFactory as _


class DexterityFormMixin(object):
    """ Mixin View that provides extra methods for custom Add/Edit Dexterity
        forms.
    """

    def __getitem__(self, key, silent=False):
        """ Allows us to get field values from the template.
            For example using either view/title or view['title']

            Enables us to have one form for both add/edit
        """
        if IAddForm.providedBy(self):
            return self.request.get(key, None)

        if key == 'macros':
            return self.index.macros

        if key in self.request:
            return self.request.get(key)

        context = aq_inner(self.context)
        if hasattr(self.context, key):
            return getattr(context, key)

        elif shasattr(context, 'Schema'):
            field = context.Schema().get(key)
            if field is not None:
                return field.get(context)

        if not silent:
            raise KeyError('Could not get key %s in the request or context'
                           % key)


class AddForm(add.DefaultAddForm, DexterityFormMixin):
    """ Custom add form for the Document content type.

        It's not necessary to override all the methods below, but we leave them
        there for now as reference.
    """
    template = ViewPageTemplateFile('templates/edit_document.pt')

    def render(self):
        """ The "contents" attribute of the AddView gets populated with the
            return results of this method.
        """
        return super(AddForm, self).render()

    def update(self):
        return super(AddForm, self).update()

    def extractData(self, setErrors=True):
        exclude_from_nav_id = ('form.widgets.IExcludeFromNavigation.exclude_'
                               'from_nav')
        if exclude_from_nav_id not in self.request:
            # XXX: This is a required field, but not in the form. Not yet sure
            # what the right approach to deal with it is.
            # Either we deal with it here, or add a hidden field in the
            # template.
            self.request.form[exclude_from_nav_id] = 'selected'
        return super(AddForm, self).extractData()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        return super(EditForm, self).handleAdd(self, action)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        return super(AddForm, self).handleCancel(self, action)


class AddView(add.DefaultAddView):
    """ Custom add view for the Document content type.

        It's not necessary to override all the methods below, but we leave them
        there for now as reference.
    """
    form = AddForm


class EditForm(edit.DefaultEditForm, DexterityFormMixin):
    """ Custom edit form for the Document content type.

        It's not necessary to override all the methods below, but we leave them
        there for now as reference.
    """
    template = ViewPageTemplateFile('templates/edit_document.pt')

    def render(self):
        """ The "contents" attribute of the AddView gets populated with the
            return results of this method.
        """
        return super(EditForm, self).render()


class EditView(edit.DefaultEditView):
    """ Custom edit view for the Document content type.
    """
    form = EditForm
