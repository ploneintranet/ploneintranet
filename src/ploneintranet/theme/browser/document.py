from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from ploneintranet.theme import _
from ploneintranet.theme.browser import views


class AddForm(add.DefaultAddForm, views.DexterityFormMixin):
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
        exclude_from_nav = ''
        if not self.request.get(exclude_from_nav):
            # XXX: This is a required field, but not in the form. Not yet sure
            # what the right approach to deal with it is.
            # Either we deal with it here, or add a hidden field in the
            # template.
            self.request.form[exclude_from_nav] = 'selected'
        return super(AddForm, self).extractData()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleAdd(self, action):
        return super(AddForm, self).handleAdd(self, action)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        return super(AddForm, self).handleCancel(self, action)


class AddView(add.DefaultAddView):
    """ Custom add view for the Document content type.

        It's not necessary to override all the methods below, but we leave them
        there for now as reference.
    """
    form = AddForm


class EditForm(edit.DefaultEditForm, views.DexterityFormMixin):
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
