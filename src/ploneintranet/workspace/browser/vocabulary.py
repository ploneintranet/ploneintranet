from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads
from ploneintranet.network.browser.vocabulary import PersonalizedVocabularyView


class WorkspaceVocabularyView(PersonalizedVocabularyView):

    def __call__(self):
        """ Extract the value for "results" from the JSON string returned from
        the default @@getVocabulary view, so that it can be used by
        pat-autosuggest.
        """
        vocab_json = super(WorkspaceVocabularyView, self).__call__()
        if vocab_json:
            vocab_obj = json_loads(vocab_json)
            results = vocab_obj.get('results')
            if results:
                return json_dumps(results)
