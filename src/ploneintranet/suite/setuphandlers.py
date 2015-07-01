# -*- coding: utf-8 -*-
import csv
import copy
import json
import logging
import os
import random
import time
import traceback
import transaction

import loremipsum
from DateTime import DateTime
from collective.workspace.interfaces import IWorkspace
from datetime import datetime, timedelta
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
# from plone.uuid.interfaces import IUUID
from zope.component import getUtility, queryUtility
from zope.interface import Invalid

from ploneintranet import api as pi_api
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.statusupdate import StatusUpdate
from ploneintranet.network.behaviors.metadata import IDublinCore
from ploneintranet.network.interfaces import INetworkTool


log = logging.getLogger(__name__)


def testing(context):
    """
    Important!
    We do not want to have users with global roles such as Editor or
    Contributor in out test setup.
    """
    if context.readDataFile('ploneintranet.suite_testing.txt') is None:
        return
    log.info("testcontent setup")

    # plone.api.env.test_mode doesn't support collective.xmltestreport
    is_test = False
    for frame in traceback.extract_stack():
        if 'testrunner' in frame[0] or 'testreport/runner' in frame[0]:
            is_test = True
            break

    # commits are needed in interactive but break in test mode
    if is_test:
        commit = lambda: None
    else:
        commit = transaction.commit

    log.info("create_users")
    users = users_spec(context)
    create_users(context, users, 'avatars')
    commit()

    log.info("create workspaces")
    workspaces = workspaces_spec(context)
    create_workspaces(workspaces)
    commit()

    log.info("create caseworkspaces")
    caseworkspaces = caseworkspaces_spec(context)
    create_caseworkspaces(caseworkspaces)
    commit()

    log.info("create library content")
    library = library_spec(context)
    create_library_content(None, library)
    commit()

    log.info("create microblog stream")
    stream_json = os.path.join(context._profile_path, 'stream.json')
    with open(stream_json, 'rb') as stream_json_data:
        stream = json.load(stream_json_data)
    create_stream(context, stream, 'files')
    commit()

    log.info("done.")


def users_spec(context):
    users_csv_file = os.path.join(context._profile_path, 'users.csv')
    users = []
    with open(users_csv_file, 'rb') as users_csv_data:
        reader = csv.DictReader(users_csv_data)
        for user in reader:
            user = {
                k: v.decode('utf-8') for k, v in user.iteritems()
            }
            if not user.get('email', '').strip():
                user['email'] = '{}@example.com'.format(decode(user['userid']))
            user['follows'] = [
                decode(u) for u in user['follows'].split(' ') if u
            ]
            users.append(user)
    return users


def create_users(context, users, avatars_dir, force=False):
    """Creates user from the given list of dictionaries.

    ``context`` is the step context.

    ``users`` is a list of dictionaries each containing the following keys:

      * userid
      * fullname
      * email
      * location
      * description
      * follows (a list of userids followed)

    ``avatars_dir`` is a directory where for each userid
    there is a ``$userid.jpg`` file.
    """
    for i, user in enumerate(users):
        email = decode(user['email'])
        userid = decode(user['userid'])
        portrait_filename = '{}.jpg'.format(userid)
        fullname = user.get('fullname', u"Anon Ymous {}".format(i))
        firstname, lastname = fullname.split(' ', 1)
        properties = {
            'fullname': fullname,
            'first_name': firstname,
            'last_name': lastname,
            'location': user.get('location', u"Unknown"),
            'description': user.get('description', u"")
        }
        try:
            profile = pi_api.userprofile.create(
                username=userid,
                email=email,
                password='secret',
                approve=True,
                properties=properties,
            )
            log.info('Created user {}'.format(userid))
        except Invalid:
            # Already exists

            if not force:
                log.info("users already configured. skipping for speed")
                return

            # update
            profile = pi_api.userprofile.get(userid)
            for key, value in properties.items():
                if key != 'fullname':  # now this field is calculated
                    setattr(profile, key, value)
            log.info('Updated user {}'.format(userid))

        portrait_path = os.path.join(avatars_dir, portrait_filename)
        portrait = context.openDataFile(portrait_path)
        if portrait:

            image = NamedBlobImage(
                data=portrait.read(),
                filename=portrait_filename.decode('utf-8'))
            profile.portrait = image
        else:
            log.warning(
                'Missing portrait file for {}: {}'.format(
                    userid,
                    portrait_filename
                )
            )

    # setup social network
    graph = queryUtility(INetworkTool)
    graph.clear()
    for user in users:
        for followee in user.get('follows', []):
            graph.follow("user", decode(followee), user['userid'])


def workspaces_spec(context):
    now = datetime.now()

    budget_proposal_filename = u'budget-proposal.png'
    budget_proposal_path = os.path.join('images', budget_proposal_filename)
    budget_proposal_img = NamedBlobImage(
        data=context.openDataFile(budget_proposal_path).read(),
        filename=budget_proposal_filename
    )
    minutes_filename = u'minutes.docx'
    minutes_path = os.path.join('files', minutes_filename)
    minutes_file = NamedBlobImage(
        data=context.openDataFile(minutes_path).read(),
        filename=minutes_filename
    )

    tomorrow = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0,
                                                 microsecond=0)
    next_month = (now + timedelta(days=30)).replace(hour=9, minute=0,
                                                    second=0, microsecond=0)

    # Create workspaces
    workspaces = [
        {'title': 'Open Market Committee',
         'description': 'The OMC holds eight regularly scheduled meetings '
                        'during the year and other meetings as needed.',
         'transition': 'make_private',
         'participant_policy': 'publishers',
         'members': {'allan_neece': [u'Members'],
                     'christian_stoney': [u'Admins', u'Members'],
                     'neil_wichmann': [u'Members'],
                     'francois_gast': [u'Members'],
                     'jaimie_jacko': [u'Members'],
                     'jesse_shaik': [u'Members'],
                     'jorge_primavera': [u'Members'],
                     'silvio_depaoli': [u'Members'],
                     'lance_stockstill': [u'Members'],
                     'pearly_whitby': [u'Members'],
                     'dollie_nocera': [u'Members'],
                     'esmeralda_claassen': [u'Members'],
                     'rosalinda_roache': [u'Members'],
                     'guy_hackey': [u'Members'],
                     },
         'contents':
             [{'title': 'Manage Information',
               'type': 'Folder',
               'contents':
                   [{'title': 'Preparation of Records',
                     'description': 'How to prepare records',
                     'state': 'published',
                     'type': 'File'},
                    {'title': 'Public bodies reform',
                     'description': 'Making arrangements for the transfer of '
                                    'information, records and knowledge is a '
                                    'key part of any Machinery of Government '
                                    'change.',
                     'type': 'Document',
                     'state': 'published'},
                    {'title': 'Repurchase Agreements',
                     'description': 'A staff presentation outlined several '
                                    'approaches to raising shortterm interest '
                                    'rates when it becomes appropriate to do '
                                    'so, and to controlling the level of '
                                    'short-term interest rates ',
                     'owner': 'allan_neece',
                     'type': 'Document'},
                    {'title': u'Budget Proposal',
                     'description': (
                         u'A diagram of the factors impacting the budget and '
                         u'results'
                     ),
                     'owner': 'allan_neece',
                     'image': budget_proposal_img,
                     'type': 'Image',
                     },
                    {'title': u'Minutes',
                     'owner': 'allan_neece',
                     'description': u'Meeting Minutes',
                     'file': minutes_file,
                     'type': 'File',
                     },
                    {'title': u'Minutes Overview',
                     'owner': 'allan_neece',
                     'description': u'Meeting Minutes Overview',
                     'type': 'Document',
                     'created': now - timedelta(days=60),
                     },
                    {'title': 'Open Market Day',
                     'type': 'Event',
                     'state': 'published',
                     'start': tomorrow,
                     'end': tomorrow + timedelta(hours=8)},
                    {'title': 'Plone Conf',
                     'type': 'Event',
                     'state': 'published',
                     'start': next_month,
                     'end': next_month + timedelta(days=3, hours=8)},
                    {'title': "Yesterday's gone",
                     'type': 'Event',
                     'state': 'published',
                     'owner': 'allan_neece',
                     'start': tomorrow - timedelta(days=3),
                     'end': tomorrow - timedelta(days=2)},
                    ]},
              {'title': 'Projection Materials',
               'type': 'Folder',
               'contents':
                   [{'title': 'Projection Material',
                     'type': 'File'}]},
              {'title': 'Future Event',
               'type': 'Event',
               'start': now + timedelta(days=7),
               'end': now + timedelta(days=14)},
              {'title': 'Past Event',
               'type': 'Event',
               'start': now + timedelta(days=-7),
               'end': now + timedelta(days=-14)},
              ],
         },
        {'title': 'Parliamentary papers guidance',
         'description': '"Parliamentary paper" is a term used to describe a '
                        'document which is laid before Parliament. Most '
                        'government organisations will produce at least one '
                        'parliamentary paper per year.',
         'transition': 'make_private',
         'participant_policy': 'producers',
         'members': {'allan_neece': [u'Members'],
                     'christian_stoney': [u'Admins', u'Members'],
                     'francois_gast': [u'Members'],
                     'jaimie_jacko': [u'Members'],
                     'fernando_poulter': [u'Members'],
                     'jesse_shaik': [u'Members'],
                     'jorge_primavera': [u'Members'],
                     'silvio_depaoli': [u'Members'],
                     'kurt_weissman': [u'Members'],
                     'esmeralda_claassen': [u'Members'],
                     'rosalinda_roache': [u'Members'],
                     'guy_hackey': [u'Members'],
                     },
         'contents':
            [{'title': 'Test Document',
              'description': 'A document just for testing',
              'type': 'Document'}]
         },
        {'title': u'Shareholder information',
         'description': u'"Shareholder information" contains all documents, '
            u'papers and diagrams for keeping shareholders informed about the '
            u'current state of affairs.',
         'transition': 'make_private',
         'participant_policy': 'consumers',
         'members': {'allan_neece': [u'Members'],
                     'christian_stoney': [u'Admins', u'Members'],
                     'francois_gast': [u'Members'],
                     'jaimie_jacko': [u'Members'],
                     'fernando_poulter': [u'Members'],
                     'jesse_shaik': [u'Members'],
                     'jorge_primavera': [u'Members'],
                     'silvio_depaoli': [u'Members'],
                     'kurt_weissman': [u'Members'],
                     'esmeralda_claassen': [u'Members'],
                     'rosalinda_roache': [u'Members'],
                     'guy_hackey': [u'Members'],
                     },
         'contents':
            [{'title': 'Test Document',
              'description': 'A document just for testing',
              'type': 'Document',
              'state': 'published'}]
         },
        {'title': u'Service announcements',
         'description': u'Public service announcements can be found here.',
         'transition': 'make_open',
         'participant_policy': 'consumers',
         'members': {'allan_neece': [u'Members'],
                     'christian_stoney': [u'Admins', u'Members'],
                     'francois_gast': [u'Members'],
                     'jaimie_jacko': [u'Members'],
                     'fernando_poulter': [u'Members'],
                     'jesse_shaik': [u'Members'],
                     'jorge_primavera': [u'Members'],
                     'silvio_depaoli': [u'Members'],
                     'kurt_weissman': [u'Members'],
                     'esmeralda_claassen': [u'Members'],
                     'rosalinda_roache': [u'Members'],
                     'guy_hackey': [u'Members'],
                     },
         'contents':
            [{'title': 'Terms and conditions',
              'description': 'A document just for testing',
              'type': 'Document',
              'state': 'published'},
             {'title': 'Customer satisfaction survey',
              'description': 'A private document',
              'type': 'Document'},
             ]
         },
    ]
    return workspaces


def create_workspaces(workspaces, force=False):
    portal = api.portal.get()
    ws_folder = portal['workspaces']

    if not force and ('ploneintranet.workspace.workspacefolder'
                      in [x.portal_type for x in ws_folder.objectValues()]):
        log.info("workspaces already setup. skipping for speed.")
        return

    for w in workspaces:
        contents = w.pop('contents', None)
        members = w.pop('members', {})
        transition = w.pop('transition', 'make_private')
        participant_policy = w.pop('participant_policy', 'consumers')
        workspace = api.content.create(
            container=ws_folder,
            type='ploneintranet.workspace.workspacefolder',
            **w
        )
        api.content.transition(obj=workspace, transition=transition)
        workspace.participant_policy = participant_policy
        if contents is not None:
            create_ws_content(workspace, contents)
        for (m, groups) in members.items():
            IWorkspace(workspace).add_to_team(user=m, groups=set(groups))


def caseworkspaces_spec(context):
    now = datetime.now()
    caseworkspaces = [{
        'title': 'Minifest',
        'description': 'Nicht budgetierte einmalige Beiträge. Verein DAMP. '
                       'Finanzielle Unterstützung des MinistrantInnen-Fest '
                       'vom 7. September 2014 in St. Gallen.',
        'members': {'allan_neece': [u'Members'],
                    'christian_stoney': [u'Admins', u'Members']},
        'contents': [{
            'title': 'Basisdatenerfassung',
            'type': 'todo',
            'description': 'Erfassung der Basis-Absenderdaten',
            'milestone': 'new',
        }, {
            'title': 'Hintergrundcheck machen',
            'type': 'todo',
            'description': 'Hintergrundcheck durchführen ob die Organisation '
                           'förderungswürdig ist.',
            'milestone': 'in_progress',
        }, {
            'title': 'Finanzcheck bzgl. früherer Zuwendungen',
            'type': 'todo',
            'description': 'Überprüfe wieviel finanzielle Zuwendung in den '
                           'vergangenen 5 Jahren gewährt wurde.',
            'milestone': 'in_progress',
        }, {
            'title': 'Meinung Generalvikar einholen',
            'type': 'todo',
            'description': 'Meinung des Generalvikars zum Umfang der '
                           'Förderung einholen.',
            'milestone': 'in_progress',
        }, {
            'title': 'Protokoll publizieren',
            'type': 'todo',
            'description': 'Publizieren des Beschlusses im Web - falls '
                           'öffentlich.',
            'milestone': 'decided',
        }, {
            'title': 'Supporting Materials',
            'type': 'Folder',
            'contents': [{
                'title': '',
                'type': 'File'
            }]
        }, {
            'title': 'Future Council Meeting',
            'type': 'Event',
            'start': now + timedelta(days=7),
            'end': now + timedelta(days=14)
        }, {
            'title': 'Past Council Meeting',
            'type': 'Event',
            'start': now + timedelta(days=-7),
            'end': now + timedelta(days=-14)
        }],
    }]
    return caseworkspaces


def create_caseworkspaces(caseworkspaces, force=False):
    portal = api.portal.get()
    pwft = api.portal.get_tool("portal_placeful_workflow")

    if 'workspaces' not in portal:
        ws_folder = api.content.create(
            container=portal,
            type='ploneintranet.workspace.workspacecontainer',
            title='Workspaces'
        )
        api.content.transition(ws_folder, 'publish')
    else:
        ws_folder = portal['workspaces']

    if not force and ('ploneintranet.workspace.case'
                      in [x.portal_type for x in ws_folder.objectValues()]):
        log.info("caseworkspaces already setup. skipping for speed.")
        return

    for w in caseworkspaces:
        contents = w.pop('contents', None)
        members = w.pop('members', [])
        caseworkspace = api.content.create(
            container=ws_folder,
            type='ploneintranet.workspace.case',
            **w
        )
        wfconfig = pwft.getWorkflowPolicyConfig(caseworkspace)
        wfconfig.setPolicyIn('case_workflow')

        if contents is not None:
            create_ws_content(caseworkspace, contents)
        for (m, groups) in members.items():
            IWorkspace(
                caseworkspace).add_to_team(user=m, groups=set(groups))


def create_ws_content(parent, contents):
    for content in contents:
        sub_contents = content.pop('contents', None)
        owner = content.pop('owner', None)
        state = content.pop('state', None)
        obj = api.content.create(
            container=parent,
            **content
        )
        if owner is not None:
            api.user.grant_roles(
                username=owner,
                roles=['Owner'],
                obj=obj,
            )
            obj.reindexObject()
        if state is not None:
            api.content.transition(obj, to_state=state)
        if sub_contents is not None:
            create_ws_content(obj, sub_contents)


def library_spec(context):
    hr = {'type': 'ploneintranet.library.section',
          'title': 'Human Resources',
          'description': 'Information from the HR department',
          'contents': [
              {'type': 'ploneintranet.library.folder',
               'title': 'Leave policies',
               'description': 'Holidays and sick leave',
               'contents': [
                   {'type': 'Document',
                    'title': 'Holidays',
                    'desciption': 'Yearly holiday allowance'},
                   {'type': 'Document',
                    'title': 'Sick Leave',
                    'desciption': ("You're not feeling too well, "
                                   "here's what to do")},
                   {'type': 'Document',
                    'title': 'Pregnancy',
                    'desciption': 'Expecting a child?'},
               ]},
          ]}
    mixed_contents = []
    for i in range(3):
        mixed_contents.append({'type': 'ploneintranet.library.folder'})
    for i in range(5):
        mixed_contents.append({'type': 'Document'})
    mixedfolder = {'type': 'ploneintranet.library.folder',
                   'contents': mixed_contents}
    for i in range(3):
        # leave policies
        hr['contents'][0]['contents'].append(mixedfolder)
    for i in range(3):
        hr['contents'].append(mixedfolder)
    library = [hr]
    for i in range(4):
        library.append(
            {'type': 'ploneintranet.library.section',
             'contents': [mixedfolder] * 5}
        )
    return library


library_tags = ('EU', 'Spain', 'UK', 'Belgium', 'confidential', 'onboarding',
                'budget', 'policy', 'administration', 'press')


idcounter = 0


def create_library_content(parent, spec, force=False):
    if parent is None:
        # initial call
        portal = api.portal.get()
        parent = portal.library
        api.user.grant_roles(
            username='alice_lindstrom',
            roles=['Contributor', 'Reviewer', 'Editor'],
            obj=portal.library
        )
        api.content.transition(portal.library, 'publish')
        # check only on initial call
        if not force and len(portal.library.objectIds()) > 0:
            log.info("library already setup. skipping for speed.")
            return

    # recursively called
    while spec:
        # avoiding side effects here cost me 4 hours!!
        item = copy.deepcopy(spec.pop(0))
        contents = item.pop('contents', None)
        if 'title' not in item:
            global idcounter
            idcounter += 1
            item['title'] = 'Lorem Ipsum %s' % idcounter
        if 'description' not in item:
            item['description'] = loremipsum.get_sentence()
        if item['type'] in ('Document',):
            raw_text = "\n\n".join(loremipsum.get_paragraphs(3))
            item['text'] = RichTextValue(raw=raw_text,
                                         mimeType='text/plain',
                                         outputMimeType='text/x-html-safe')

        obj = create_as('alice_lindstrom', container=parent, **item)
        wrapped = IDublinCore(obj)
        wrapped.subjects = random.sample(library_tags, random.choice(range(4)))
        api.content.transition(obj, 'publish')
        if contents:
            create_library_content(obj, contents)


def create_stream(context, stream, files_dir):
    contexts_cache = {}
    microblog = queryUtility(IMicroblogTool)
    if len([x for x in microblog.keys()]) > 0:
        log.info("microblog already setup. skipping for speed.")
        return

    like_tool = getUtility(INetworkTool)
    microblog.clear()
    for status in stream:
        kwargs = {}
        if status['context']:
            if status['context'] not in contexts_cache:
                contexts_cache[status['context']] = api.content.get(
                    path='/' + decode(status['context']).lstrip('/')
                )
            kwargs['context'] = contexts_cache[status['context']]
        status_obj = StatusUpdate(status['text'], **kwargs)
        status_obj.userid = status['user']
        status_obj.creator = api.user.get(
            username=status['user']
        ).getUserName()
        offset_time = status['timestamp'] * 60
        status_obj.id -= int(offset_time * 1e6)
        status_obj.date = DateTime(time.time() - offset_time)
        # THIS BREAKS BECAUSE docconv.client.async.queueConversionJob FIXME
        # if 'attachment' in status:
        #     _definition = status['attachment']
        #     _filename = os.path.join(files_dir, _definition['filename'])
        #     _data = context.readDataFile(_filename)
        #     attachment_obj = create_attachment(_filename, _data)
        #     attachments = IAttachmentStorage(status_obj)
        #     attachments.add(attachment_obj)
        microblog.add(status_obj)

        # like some status-updates
        if 'likes' in status:
            for user_id in status['likes']:
                like_tool.like(
                    "update",
                    user_id=user_id,
                    item_id=str(status_obj.id),

                )


def decode(value):
    if isinstance(value, unicode):
        return value.encode('utf-8')
    return value


def create_as(userid, *args, **kwargs):
    """Call api.content.create as a different user
    """
    obj = None
    with api.env.adopt_user(username=userid):
        try:
            obj = api.content.create(*args, **kwargs)
        except:
            # we still need to know what happend
            raise
    return obj
