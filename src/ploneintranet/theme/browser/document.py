from plone.dexterity.browser import add
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddForm(add.DefaultAddForm):
    xtemplate = ViewPageTemplateFile('templates/add_document.pt')

    def render(self):
        return super(AddForm, self).render()

    def extractData(self, setErrors=True):
        """See interfaces.IForm"""
        return super(AddForm, self).extractData()


class AddView(add.DefaultAddView):
    form = AddForm
