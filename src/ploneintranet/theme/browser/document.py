from plone.dexterity.browser import add
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class AddForm(add.DefaultAddForm):
    template = ViewPageTemplateFile('templates/add_document.pt')

    def render(self):
        """ The "contents" attribute of the AddView gets populated with the
            return results of this method.
        """
        return super(AddForm, self).render()

    def updat(self):
        return super(AddForm, self).update()

    def updateWidgets(self):
        return super(AddForm, self).updateWidgets()

    def extractData(self, setErrors=True):
        return super(AddForm, self).extractData()


class AddView(add.DefaultAddView):
    form = AddForm

    def __init__(self, context, request, ti):
        return super(AddView, self).__init__(context, request, ti)

    def update(self):
        return super(AddView, self).update()

