from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_chain

# -*- coding: utf-8 -*-
from Acquisition import aq_inner

from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from datetime import datetime
from DateTime import DateTime

from urllib import quote as url_quote

from zope.i18n import translate
from zope.i18nmessageid import Message

from zope.component import createObject, queryUtility

from zope.interface import alsoProvides

from z3c.form import form, field, button, interfaces
from z3c.form.interfaces import IFormLayer
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from plone.registry.interfaces import IRegistry

from plone.app.layout.viewlets.common import ViewletBase

from plone.app.discussion import PloneAppDiscussionMessageFactory as _
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IReplies
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.interfaces import ICaptcha

from plone.app.discussion.browser.validator import CaptchaValidator

from plone.z3cform import z2
from plone.z3cform.fieldsets import extensible
from plone.z3cform.interfaces import IWrappedForm

from plonesocial.microblog.interfaces import IStatusContainer
from plonesocial.microblog.interfaces import IStatusUpdate
from plonesocial.microblog.statusupdate import StatusUpdate

COMMENT_DESCRIPTION_PLAIN_TEXT = _(
    u"comment_description_plain_text",
    default=u"You can add a comment by filling out the form below. " +
             "Plain text formatting.")

COMMENT_DESCRIPTION_MARKDOWN = _(
    u"comment_description_markdown",
    default=u"You can add a comment by filling out the form below. " +
             "Plain text formatting. You can use the Markdown syntax for " +
             "links and images.")

COMMENT_DESCRIPTION_INTELLIGENT_TEXT = _(
    u"comment_description_intelligent_text",
    default=u"You can add a comment by filling out the form below. " +
             "Plain text formatting. Web and email addresses are " +
             "transformed into clickable links.")

COMMENT_DESCRIPTION_MODERATION_ENABLED = _(
    u"comment_description_moderation_enabled",
    default=u"Comments are moderated.")


class CommentForm(extensible.ExtensibleForm, form.Form):

    ignoreContext = True  # don't use context to get widget data
    id = None
    label = _(u"Add a comment")
    fields = field.Fields(IStatusUpdate).omit('portal_type',
                                              '__parent__',
                                              '__name__',
                                              'comment_id',
                                              'mime_type',
                                              'creator',
                                              'userid',
                                              'creation_date')

    def updateFields(self):
        super(CommentForm, self).updateFields()

    def updateWidgets(self):
        super(CommentForm, self).updateWidgets()

    def updateActions(self):
        super(CommentForm, self).updateActions()
        self.actions['cancel'].addClass("standalone")
        self.actions['cancel'].addClass("hide")
        self.actions['statusupdate'].addClass("context")

    @button.buttonAndHandler(_(u"add_statusupdate_button",
                               default=u"What are you doing?"),
                             name='statusupdate')
    def handleComment(self, action):
        context = aq_inner(self.context)

## FIXME
        # Check if conversation is enabled on this content object
        if not self.__parent__.restrictedTraverse(
            '@@conversation_view').enabled():
            raise Unauthorized("Discussion is not enabled for this content "
                               "object.")

        # Validation form
        data, errors = self.extractData()
        if errors:
            return

        portal_membership = getToolByName(self.context, 'portal_membership')

        # Create comment
        comment = createObject('plone.Comment')
        # Set comment attributes (including extended comment form attributes)
        for attribute in self.fields.keys():
            setattr(comment, attribute, data[attribute])

        # Set comment author properties for anonymous users or members
        can_reply = getSecurityManager().checkPermission('Reply to item',
                                                         context)
        portal_membership = getToolByName(self.context, 'portal_membership')
        if not portal_membership.isAnonymousUser() and can_reply:
            # Member
            member = portal_membership.getAuthenticatedMember()
            username = member.getUserName()
            email = member.getProperty('email')
            fullname = member.getProperty('fullname')
            if not fullname or fullname == '':
                fullname = member.getUserName()
            # memberdata is stored as utf-8 encoded strings
            elif isinstance(fullname, str):
                fullname = unicode(fullname, 'utf-8')
            if email and isinstance(email, str):
                email = unicode(email, 'utf-8')
            comment.creator = fullname
            comment.author_username = username
            comment.author_name = fullname
            comment.author_email = email
            comment.creation_date = datetime.utcnow()
            comment.modification_date = datetime.utcnow()
        else:  # pragma: no cover
            raise Unauthorized("Anonymous user tries to post a status update, "
                "or user does not have the "
                "'reply to item' permission.")

        container = IStatusContainer(self.__parent__)  # make this getSite
        # Fake a new activity with some random text, just to get a
        # bit of content.
        import random
        import string
        text = ''.join(random.sample(string.printable,
                                      random.randint(8, 20)))
        # pick between zero and two tags:
        possible_tags = ['random', 'fuzzy', 'beer']
        tags = random.sample(possible_tags, random.randint(0, 2))
        text = data['text']
        status = StatusUpdate(text, tags)

        # debugging only
        container.clear()

        # save the status update
        container.add(status)

        # Redirect to portal home
        self.request.response.redirect(self.action)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass  # pragma: no cover


class StatusForm(CommentForm):
    """
    re-add the button and handler on a different name
    so we don't get double form processing
    and double comment creation
    """
    form.extends(CommentForm, ignoreButtons=True, ignoreHandlers=True)

    def updateActions(self):
        super(CommentForm, self).updateActions()
        self.actions['cancel'].addClass("standalone")
        self.actions['cancel'].addClass("hide")
        self.actions['status'].addClass("context")

    @button.buttonAndHandler(_(u"add_comment_button", default=u"Comment"),
                             name='status')
    def handleStatus(self, action):
        # unwrap CommentForm.handleComment from it's decorator
        # depends on z3c.form.button.Handler implementation detail
        CommentForm.handleComment.func(self, action)

    @button.buttonAndHandler(_(u"Cancel"))
    def handleCancel(self, action):
        # This method should never be called, it's only there to show
        # a cancel button that is handled by a jQuery method.
        pass  # pragma: no cover


class CommentsViewlet(ViewletBase):

    form = CommentForm
    index = ViewPageTemplateFile('status.pt')

    def update(self):
        super(CommentsViewlet, self).update()
        if self.is_discussion_allowed() and \
           (self.is_anonymous() and self.anonymous_discussion_allowed() \
            or self.can_reply()):
            z2.switch_on(self, request_layer=IFormLayer)
            self.form = self.form(aq_inner(self.context), self.request)
            alsoProvides(self.form, IWrappedForm)
            self.form.update()

    # view methods

    def can_reply(self):
        """Returns true if current user has the 'Reply to item' permission.
        """
        return getSecurityManager().checkPermission('Reply to item',
                                                    aq_inner(self.context))

    def can_manage(self):
        """We keep this method for <= 1.0b9 backward compatibility. Since we do
           not want any API changes in beta releases.
        """
        return self.can_review()

    def can_review(self):
        """Returns true if current user has the 'Review comments' permission.
        """
        return getSecurityManager().checkPermission('Review comments',
                                                    aq_inner(self.context))

    def is_discussion_allowed(self):
        context = aq_inner(self.context)
        return context.restrictedTraverse('@@conversation_view').enabled()

    def comment_transform_message(self):
        """Returns the description that shows up above the comment text,
           dependent on the text_transform setting and the comment moderation
           workflow in the discussion control panel.
        """
        context = aq_inner(self.context)
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)

        # text transform setting
        if settings.text_transform == "text/x-web-intelligent":
            message = translate(Message(COMMENT_DESCRIPTION_INTELLIGENT_TEXT),
                                context=self.request)
        elif settings.text_transform == "text/x-web-markdown":
            message = translate(Message(COMMENT_DESCRIPTION_MARKDOWN),
                                context=self.request)
        else:
            message = translate(Message(COMMENT_DESCRIPTION_PLAIN_TEXT),
                                context=self.request)

        # comment workflow
        wftool = getToolByName(context, "portal_workflow", None)
        workflow_chain = wftool.getChainForPortalType('Discussion Item')
        if workflow_chain:
            comment_workflow = workflow_chain[0]
            comment_workflow = wftool[comment_workflow]
            # check if the current workflow implements a pending state. If this
            # is true comments are moderated
            if 'pending' in comment_workflow.states:
                message = message + " " + \
                    translate(Message(COMMENT_DESCRIPTION_MODERATION_ENABLED),
                              context=self.request)

        return message

    def has_replies(self, workflow_actions=False):
        """Returns true if there are replies.
        """
        if self.get_replies(workflow_actions) is not None:
            try:
                self.get_replies(workflow_actions).next()
                return True
            except StopIteration:  # pragma: no cover
                pass
        return False

    def get_replies(self, workflow_actions=False):
        """Returns all replies to a content object.

        If workflow_actions is false, only published
        comments are returned.

        If workflow actions is true, comments are
        returned with workflow actions.
        """
        context = aq_inner(self.context)
        conversation = IConversation(context)

        wf = getToolByName(context, 'portal_workflow')

        # workflow_actions is only true when user
        # has 'Manage portal' permission

        def replies_with_workflow_actions():
            # Generator that returns replies dict with workflow actions
            for r in conversation.getThreads():
                comment_obj = r['comment']
                # list all possible workflow actions
                actions = [a for a in wf.listActionInfos(object=comment_obj)
                               if a['category'] == 'workflow' and a['allowed']]
                r = r.copy()
                r['actions'] = actions
                yield r

        def published_replies():
            # Generator that returns replies dict with workflow status.
            for r in conversation.getThreads():
                comment_obj = r['comment']
                workflow_status = wf.getInfoFor(comment_obj, 'review_state')
                if workflow_status == 'published':
                    r = r.copy()
                    r['workflow_status'] = workflow_status
                    yield r

        # Return all direct replies
        if conversation.total_comments > 0:
            if workflow_actions:
                return replies_with_workflow_actions()
            else:
                return published_replies()

    def get_commenter_home_url(self, username=None):
        if username is None:
            return None
        else:
            return "%s/author/%s" % (self.context.portal_url(), username)

    def get_commenter_portrait(self, username=None):

        if username is None:
            # return the default user image if no username is given
            return 'defaultUser.gif'
        else:
            portal_membership = getToolByName(self.context,
                                              'portal_membership',
                                              None)
            return portal_membership.getPersonalPortrait(username)\
                   .absolute_url()

    def anonymous_discussion_allowed(self):
        # Check if anonymous comments are allowed in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.anonymous_comments

    def show_commenter_image(self):
        # Check if showing commenter image is enabled in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.show_commenter_image

    def is_anonymous(self):
        portal_membership = getToolByName(self.context,
                                          'portal_membership',
                                          None)
        return portal_membership.isAnonymousUser()

    def login_action(self):
        return '%s/login_form?came_from=%s' % \
            (self.navigation_root_url,
             url_quote(self.request.get('URL', '')),)

    def format_time(self, time):
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        util = getToolByName(self.context, 'translation_service')
        zope_time = DateTime(time.isoformat())
        return util.toLocalizedTime(zope_time, long_format=True)


class StatusViewlet(CommentsViewlet):
    """Subclass the p.a.discussion comments viewlet
    and change it's behaviour to suit our purposes."""

    form = StatusForm
    index = ViewPageTemplateFile('status.pt')

    comment_transform_message = "What's on your mind?"

    def __init__(self, compact, *args, **kwargs):
        CommentsViewlet.__init__(self, *args, **kwargs)
        self.compact = compact
        # force microblog context to SiteRoot singleton
        for obj in aq_chain(self.context):
            if IPloneSiteRoot.providedBy(obj):
                self.context = obj
                return
