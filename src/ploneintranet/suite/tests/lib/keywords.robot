*** Keywords ***

Prepare test browser
    Open test browser
    Set window size  1280  1024

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}

I am logged in as site administrator
    Element should be visible  css=body.userrole-site-administrator

I am logged in as the user ${userid}
    Go To  ${PLONE_URL}/login
    Input text  name=__ac_name  ${userid}
    Input text  name=__ac_password  secret
    Click Element  css=#login-panel button[type=submit]

# add content keyword that supports
# both dexterity and archetypes
Add content item
    [arguments]  ${content_type}  ${title}
    Open add new menu
    Click link  link=${content_type}
    Fill text field  Title  ${title}
    Click button  name=form.buttons.save
    Page should contain  Item created
    Page should contain  ${title}
    ${location} =  Get Location
    [return]  ${location}

# Fill a text field
# Field is matched via a preceding <label>
Fill text field
    [arguments]  ${field_label}   ${text}
    Input Text  xpath=//form//div/input[preceding-sibling::label[contains(text(), '${field_label}')]]  ${text}

Add workspace
    [arguments]  ${title}
    Go to  ${PLONE_URL}/workspaces/++add++ploneintranet.workspace.workspacefolder
    Input text  name=form.widgets.IBasic.title  ${title}
    Click Button  Save
    Page Should Contain  Item created

Maneuver to
    [arguments]  ${title}
    Go to homepage
    Click link  jquery=a:contains("${title}")

I can reload the page
    Reload Page

I open the Dashboard
    Go to  ${PLONE_URL}/dashboard.html
    Comment  auto bypass CSRF errors, typically in bin/pybot manual tests
    Run Keyword And Ignore Error  Click Element  xpath=//input[@name='form.button.confirm']
    Wait Until Page Contains Element  css=#dashboard

I am in a workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Open Market Committee Workspace

I am in a Producers workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Open Parliamentary Papers Guidance Workspace

I am in a Producers workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Open Parliamentary Papers Guidance Workspace

I am in a Consumers workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Shareholder Information Workspace

I am in a Consumers workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Shareholder Information Workspace

I am in a workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Open Market Committee Workspace

I am in an open workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Service Announcements Workspace

I am in an open workspace as a non-member
    I am logged in as the user alice_lindstrom
    I go to the Service Announcements Workspace

I go to the Open Market Committee Workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Open Market Committee

I go to the Example Case
    Go To  ${PLONE_URL}/workspaces/example-case
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Example Case

I go to the Open Parliamentary Papers Guidance Workspace
    Go To  ${PLONE_URL}/workspaces/parliamentary-papers-guidance
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Parliamentary papers guidance

I go to the Shareholder Information Workspace
    Go To  ${PLONE_URL}/workspaces/shareholder-information
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Shareholder information

I go to the Service Announcements Workspace
    Go To  ${PLONE_URL}/workspaces/service-announcements
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Service announcements

I go to the Archived Workspace
    Go To  ${PLONE_URL}/workspaces/archived-workspace
    Wait Until Page Does Not Contain Element  css=.injecting-content

I can go to the Open Market Committee Workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee

I can go to the Example Case
    Go To  ${PLONE_URL}/workspaces/example-case

I am redirected to the login page
    Location Should Contain  require_login

I open the password reset form
    Go To  ${PLONE_URL}/pwreset_form

The page is not found
    Page should contain  This page does not seem to exist

I cannot reset my password with an illegal request posing as
    [arguments]    ${user_name}
    Page should contain  Set your password
    Input text  css=input#userid  ${user_name}
    Input text  css=input#password  impostor
    Input text  css=input#password2  impostor
    Click button  Set my password
    Wait until page contains  Error setting password


# *** Posting and stream related keywords ***

I can see updates by
    [arguments]  ${user_fullname}
    Element should be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//div[@class='post-header']//h4[text()='${user_fullname}']/..

I cannot see updates by
    [arguments]  ${user_fullname}
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//div[@class='post-header']//h4[text()='${user_fullname}']/..

I can follow the profile link for user
    [arguments]  ${user_fullname}
    [Documentation]  We click on the second post item, because we know that Christian Stoney has 2 posts and the 1st post can be hidden by a stupid scroll issue after activating the network filter
    Click Link  xpath=//div[@id='activity-stream']//div[@class='post item'][2]//div[@class='post-header']//h4[text()='${user_fullname}']/..

I can see updates tagged
    [arguments]  ${tag}
    Page Should Contain Link  \#${tag}

I cannot see updates tagged
    [arguments]  ${tag}
    Page Should Not Contain Link  \#${tag}

I click the tag link
    [arguments]  ${tag}
    Click Link  \#${tag}

I can toggle following the tag
    Click Element  css=#follow-function button
    Wait Until Page Does Not Contain Element  css=.injecting-content

I am following the tag
    Page Should Contain Element  css=#follow-function button.active

I am not following the tag
    Page Should Not Contain Element  css=#follow-function button.active

I can toggle following the user
    Click Element  css=#portlet-follow form button
    Wait Until Page Does Not Contain Element  css=.injecting-content

I filter the stream as
    [arguments]  ${stream_filter}
    Click element  xpath=//select[@name='stream_filter']//option[@value='${stream_filter}']
    Wait until page contains element  xpath=//select[@name='stream_filter']//option[@value='${stream_filter}'][@selected='selected']

The message is visible as new status update
    [arguments]  ${message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]

The reply is visible
    [arguments]  ${message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='comment-content']//p[contains(text(), '${message}')][1]

The message is not visible
    [arguments]  ${message}
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]

The message is visible as new status update that mentions the user
    [arguments]  ${message}  ${username}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p//a[contains(text(), '@${username}')][1]

The message is visible as new status update and includes the tag
    [arguments]  ${message}  ${tag}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p//a[contains(text(), '#${tag}')][1]

The status update only appears once
    [arguments]  ${message}
    Element should be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][2]

The message is visible after a reload
    [arguments]  ${message}
    ${location} =  Get Location
    Go to    ${location}
    The message is visible as new status update    ${message}

I post a reply on a status update
    [arguments]  ${message}  ${reply_message}
    Click Element  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')]//..//..//../textarea[contains(@class, 'pat-content-mirror')]
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')]//..//..//../button[@name='form.buttons.statusupdate']
    Input Text  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')]//..//..//../textarea[contains(@class, 'pat-content-mirror')]  ${reply_message}
    Click button  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')]//..//..//../button[@name='form.buttons.statusupdate']

The reply is visible as a comment
    [arguments]  ${message}  ${reply_message}
    Wait Until Element Is visible  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message}')][1]//..//..//..//div[@class='comments']//section[@class='comment-content']//p[contains(text(), '${reply_message}')]

The reply is not visible
    [arguments]  ${message}
    Element should not be visible  xpath=//div[@id='activity-stream']//div[@class='post item']//div[@class='comments']//section[@class='comment-content']//p[contains(text(), '${message}')]

The reply is visible after a reload
    [arguments]  ${message}  ${reply_message}
    ${location} =  Get Location
    Go to    ${location}
    The reply is visible as a comment  ${message}  ${reply_message}

Both replies are visible
    [arguments]  ${message}  ${reply_message1}  ${reply_message2}
    The reply is visible as a comment  ${message}  ${reply_message1}
    The reply is visible as a comment  ${message}  ${reply_message2}

Both replies are visible after a reload
    [arguments]  ${message}  ${reply_message1}  ${reply_message2}
    ${location} =  Get Location
    Go to    ${location}
    The reply is visible as a comment  ${message}  ${reply_message1}
    The reply is visible as a comment  ${message}  ${reply_message2}

I can add a tag
    [arguments]  ${tag}
    Click link    link=Add tags
    Wait Until Element Is visible    xpath=//form[@id='postbox-tags']
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag}
    [Documentation]  Wait until the temporary class 'injecting-content' has been removed, to be sure injection has completed
    Wait until page does not contain element  xpath=//form[@id='postbox-tags' and contains(@class, 'injecting-content')]
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag}')][1]
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag}')][1]
    Click element    css=textarea.pat-content-mirror

I can add a tag and search for a tag
    [arguments]  ${tag1}  ${tag2}
    Click link    link=Add tags
    Wait Until Element Is visible    xpath=//form[@id='postbox-tags']
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag1}
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag1}')][1]
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag1}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag1}')][1]
    Click element    css=input[name=tagsearch]
    Input text    css=input[name=tagsearch]  ${tag2}
    [Documentation]  Wait until the temporary class 'injecting-content' has been removed, to be sure injection has completed
    Wait until page does not contain element  xpath=//form[@id='postbox-tags' and contains(@class, 'injecting-content')]
    Wait Until Element Is visible  xpath=//form[@id='postbox-tags']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${tag2}')][1]
    Click element  xpath=//form[@id='postbox-tags']//label/a/strong[contains(text(), '${tag2}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '#${tag2}')][1]
    Click element    css=textarea.pat-content-mirror

I can mention a user and search for a user
    [arguments]  ${username1}  ${username2}
    Click link    link=Mention people
    Wait Until Element Is visible    xpath=//form[@id='postbox-users']
    Click element  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username1}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '@${username1}')][1]
    Click element    css=input[name=usersearch]
    Input text    css=input[name=usersearch]  ${username2}
    [Documentation]  Wait until the temporary class 'injecting-content' has been removed, to be sure injection has completed
    Wait until page does not contain element  xpath=//form[@id='postbox-users' and contains(@class, 'injecting-content')]
    Wait Until Element Is visible  xpath=//form[@id='postbox-users']//fieldset[contains(@class, 'search-active')]//a//strong[contains(text(), '${username2}')][1]
    Click element  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username2}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(),'${username2}')][1]
    Click element    css=textarea.pat-content-mirror

The content stream is visible
    Wait until element is visible       css=#comments-document-comments

I save the document
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click button  Close
    Wait until page does not contain  Your changes have been saved

The stream contains
    [arguments]    ${text}
    Wait until page contains    ${text}

The stream links to the document
    [arguments]  ${text}
    Wait until page contains element       link=${text}

The stream does not link to the document
    [arguments]  ${text}
    Page should not contain       link=${text}

# *** Workspace related keywords ***

I can create a new workspace
    [arguments]  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal
    Input Text  xpath=//input[@name='title']  text=${title}
    Input Text  xpath=//textarea[@name='description']  text=Random description
    Click Button  Create workspace
    Wait Until Page Contains  Item created
    Click Button  Close
    Wait Until Element Is visible  css=div#activity-stream

I can see the first listed workspace is
    [arguments]  ${title}
    Wait until page contains Element  jquery=.tiles .tile:first h3:contains("${title}")

I can see the last listed workspace is
    [arguments]  ${title}
    Wait until page contains Element  jquery=.tiles .tile:last h3:contains("${title}")

I can set workspace listing order
    [arguments]  ${value}
    Select From List  css=select[name=sort]  ${value}

I can create a new template workspace
    [arguments]  ${title}
    Go To  ${PLONE_URL}/templates/++add++ploneintranet.workspace.workspacefolder
    Input Text  form.widgets.IBasic.title  New template
    Click Button  Save
    Go To  ${PLONE_URL}/workspaces

I can create a new workspace for the division
    [arguments]  ${title}  ${division}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal
    Input Text  xpath=//input[@name='title']  text=${title}
    Input Text  xpath=//textarea[@name='description']  text=Random description
    Select From List  division  ${division}
    Click Button  Create workspace
    Wait Until Page Contains  Item created
    Click Button  Close
    Wait Until Element Is visible  css=div#activity-stream

I can see the workspace belongs to division
    [arguments]  ${division}
    Wait Until Element Is Visible  xpath=//select//option[@selected='selected'][text()='${division}']

I can create a new workspace from a template
    [arguments]  ${template}  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal
    Input Text  name=title  text=${title}
    Input Text  name=description  text=Something completely different
    Select From List  workspace-type  new-template
    Wait Until Page Contains  New template
    Click Button  Create workspace
    Wait Until Page Contains  Item created


I select a file to upload
    [Documentation]  We can't drag and drop from outside the browser so it gets a little hacky here
    Execute JavaScript  jQuery('.pat-upload.upload .accessibility-options').show()
    Execute JavaScript  jQuery('.pat-upload.upload').siblings('button').show()
    Choose File  css=input[name=file]  ${UPLOADS}/bärtige_flößer.odt
    Click Element  xpath=//button[text()='Upload']

I open the sidebar documents tile
    Click Link  css=a.documents
    Wait Until Page Contains Element  css=div#workspace-documents

I can go to the sidebar info tile
    Click Link  link=Workspace settings and about
    Wait Until Page Contains  General
    Wait Until Page Contains  Workspace title
    Wait Until Page Contains  Workspace brief description

I can go to the sidebar events tile
    Click Link  link=Events
    Wait Until Element Is visible  xpath=//h3[.='Upcoming events']

I can open the workspace advanced settings tab
    Click Link  link=Workspace settings and about
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Wait until page contains  Advanced
    Click link  link=Advanced
    [Documentation]  Wait until the temporary class 'injecting' has been removed, to be sure injection has completed
    Wait until page does not contain element   xpath=//div[@id='workspace-settings']/div[contains(@class, 'tabs-content injecting')]
    Wait until page contains  Workspace e-mail address

I can open the workspace security settings tab
    Click Link  link=Workspace settings and about
    Wait until page contains  Security
    Click link  link=Security
    [Documentation]  Wait until the temporary class 'injecting' has been removed, to be sure injection has completed
    Wait until page does not contain element   xpath=//div[@id='workspace-settings']/div[contains(@class, 'tabs-content injecting')]
    Wait until page contains  Workspace policy

I can open the workspace member settings tab
    Click Link  link=Workspace settings and about
    Click link  link=Members
    [Documentation]  Wait until the temporary class 'injecting' has been removed, to be sure injection has completed
    Wait until page does not contain element   xpath=//div[@id='workspace-settings']/div[contains(@class, 'tabs-content injecting')]
    Wait until page contains element  css=#member-list

I can turn the workspace into a division
    Click element  xpath=//input[@name='is_division']/../..
    Wait until page does not contain element   xpath=//div[@id='workspace-settings']/div[contains(@class, 'tabs-content injecting')]
    [Documentation]  Wait until the temporary class 'injecting' has been removed, to be sure injection has completed
    Wait until element is visible  xpath=//input[@name='is_division' and @value='selected' and @checked='checked']/../..
    Wait until page contains  Attributes changed
    Click button  Close

I can archive the workspace
    Select checkbox  xpath=//input[@name='archival_date']
    Wait Until Page Does Not Contain Element  css=.injecting-content

I can unarchive the workspace
    Unselect checkbox  xpath=//input[@name='archival_date']
    Wait Until Page Does Not Contain Element  css=.injecting-content

I can list the workspaces grouped by division
    Go To  ${PLONE_URL}/workspaces
    Click element  xpath=//select[@name='grouping']
    Click element  xpath=//option[@value='division']
    [Documentation]  Wait until the temporary class 'injecting' has been removed, to be sure injection has completed
    Wait until page does not contain element   xpath=//span[@id='workspaces' and contains(@class, 'tabs-content injecting')]

I can list the workspaces
    Go To  ${PLONE_URL}/workspaces
    Click element  xpath=//select[@name='grouping']
    Click element  xpath=//option[@value='division']
    Wait Until Page Does Not Contain Element  css=.injecting-content

I can see the division
    [arguments]  ${title}
    Wait Until Element Is Visible  xpath=//h1[text()='${title}']

I can see the workspace
    [arguments]  ${title}
    Page should contain  ${title}

I can't see the workspace
    [arguments]  ${title}
    Page should not contain  ${title}

I can list the archived workspaces
    I can list the workspaces
    Select checkbox  xpath=//input[@name='archived']
    [Documentation]  Wait until the temporary class 'injecting' has been removed, to be sure injection has completed
    Wait until page does not contain element   xpath=//span[@id='workspaces'][contains(@class, 'injecting')]

I can set the external visibility to Open
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='external_visibility']")[0].value = 3
    Submit form  css=#sidebar-settings-security
    Wait Until Page Contains  Security
    Click link  link=Security
    Wait until page contains  The workspace can be explored by outsiders.

I can set the join policy to Admin-Managed
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='join_policy']")[0].value = 1
    Submit form  css=#sidebar-settings-security
    Wait Until Page Contains  Security
    Click link  link=Security
    Wait until page contains  Only administrators can add workspace members.

I can set the participant policy to Moderate
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='participant_policy']")[0].value = 4
    Submit form  css=#sidebar-settings-security
    Wait Until Page Contains  Security
    Click link  link=Security
    Wait until page contains  Workspace members can do everything

I can set the participant policy to Consume
    Comment  AFAICT selenium doesn't yet have support to set the value of a range input field, using JavaScript instead
    Execute JavaScript  jQuery("[name='participant_policy']")[0].value = 1
    Submit form  css=#sidebar-settings-security
    Wait Until Page Contains  Security
    Click link  link=Security
    Wait until page contains  They cannot add

I can open Esmeralda's profile
    Click Element  css=a[href$='/profiles/esmeralda_claassen']
    Wait Until Element Is visible  css=#person-timeline .sidebar

I can follow Esmeralda
    Element should contain  css=.icon-eye  Follow Esmeralda Claassen
    Click Element  css=.icon-eye
    Wait Until Page contains element  css=button[title="You are now following Esmeralda Claassen. Click to unfollow."]

I can see upcoming events
    Page Should Contain Element  xpath=//ul[@class='event-list']//a/h4[text()[contains(.,'Plone Conf')]]

Older events are hidden
    Element should be visible  jquery=div#older-events a

I can go to the sidebar tasks tile
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Tasks
    Wait Until Element Is visible  xpath=//p[.='No tasks created yet']

I create a task for
    [arguments]  ${name}
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Tasks
    Wait Until Element Is visible  css=[title="Create new task"]
    Click Element  css=[title="Create new task"]
    Wait Until Page Contains Element  css=.wizard-box
    Input Text  css=.wizard-box input[name=title]  Ciao ${name}
    Input Text  css=.wizard-box textarea[name=description]  This is for you ${name}
    Click Element  css=.wizard-box .assignee .select2-choices input
    Input Text  css=.wizard-box .assignee .select2-choices input  ${name}
    Wait Until Page Contains Element  jquery=span.select2-match:last
    Click Element  jquery=span.select2-match:last
    Input Text  css=.wizard-box input[name=due]  2020-12-31
    Click Element  css=.wizard-box #form-buttons-create
    Wait Until Page Contains Element  css=a[title="Ciao ${name}"]

Task is read only for user
    [arguments]  ${name}
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Tasks
    Wait Until Page Contains Element  css=a[title="Ciao ${name}"]
    Click Element  css=a[title="Ciao ${name}"]
    Wait Until Page Contains  This is for you ${name}
    Element Should Be Visible  jquery=input:disabled[name=due]

# workspace member sidebar
I can enable user selection
    Wait Until Page Contains Element  jquery=.quick-functions a.toggle-select
    Click Element  jquery=.quick-functions a:last

I select all members
    Click Element  css=#existing_users .select-buttons .select-all

I deselect all members
    Click Element  css=#existing_users .select-buttons .deselect-all

The batch action buttons are disabled
    Wait Until Page Contains Element  jquery=button.disabled:contains("Change role")
    Wait Until Page Contains Element  jquery=button.disabled:contains("Remove")

The batch action buttons are enabled
    Wait Until Page Contains Element  jquery=button:not('[disabled]'):contains("Change role")
    Wait Until Page Contains Element  jquery=button:not('[disabled]'):contains("Remove")

I toggle the selection of the first user
    Click Element  jquery=#member-list-items label.item.user:first

I can invite Alice to join the workspace
    Wait Until Page Contains Element  css=div.button-bar.create-buttons a.icon-user-add
    Click Link  css=div.button-bar.create-buttons a.icon-user-add
    I can invite Alice to the workspace

I can invite Alice to join the workspace from the menu
    Wait Until Page Contains Element  link=Functions
    Click Link  link=Functions
    Wait until page does not contain element   xpath=//div[@id='member-list-more-menu']/div[contains(@class, 'panel-content in-progress')]
    Wait until element is visible  xpath=//div[@id='member-list-more-menu']/div[@class='panel-content']
    Click Link  xpath=//ul[@class='menu']//a[.='Add user']
    I can invite Alice to the workspace

I can invite Alice to the workspace
    Wait until element is visible  xpath=//div[contains(@class, 'pat-modal')]//h1[text()='Add users']
    Input Text  css=li.select2-search-field input  alice
    Wait Until Element Is visible  css=span.select2-match
    Click Element  css=span.select2-match
    Click Button  Ok

I give the Consumer role to Allan
    I can open the workspace member settings tab
    Click link  xpath=//div[@id='member-list-functions']//a[text()='Select']
    Click Element  xpath=//input[@value='allan_neece']/..
    Click Button  Change role
    Wait until element is visible  //div[@class='panel-content']//select[@name='role']
    Select From List  css=select[name=role]  Consumers
    Click Button  xpath=//div[@id='document-content']//div[contains(@class, 'panel-footer')]/button[@type='submit']
    Wait until page contains element  xpath=//input[@value='allan_neece']/../a[text()='Consume']

I give the Producer role to Allan
    I can open the workspace member settings tab
    Click link  xpath=//div[@id='member-list-functions']//a[text()='Select']
    Wait until element is visible   xpath=//div[contains(@class, 'batch-functions')]//button[@value='role']
    Click Element  xpath=//input[@value='allan_neece']/..
    Click Button  Change role
    Wait until element is visible  //div[@class='panel-content']//select[@name='role']
    Select From List  css=select[name=role]  Producers
    Click Button  xpath=//div[@id='document-content']//div[contains(@class, 'panel-footer')]/button[@type='submit']
    Wait until page contains  Role updated
    Click button  Close
    Page Should Contain Element  xpath=//input[@value='allan_neece']/../a[text()='Produce']

I give the Admin role to Allan
    I can open the workspace member settings tab
    Click link  xpath=//div[@id='member-list-functions']//a[text()='Select']
    Wait until element is visible   xpath=//div[contains(@class, 'batch-functions')]//button[@value='role']
    Click Element  xpath=//input[@value='allan_neece']/..
    Click Button  Change role
    Wait until element is visible  //div[@class='panel-content']//select[@name='role']
    Select From List  css=select[name=role]  Admins
    Click Button  xpath=//div[@id='document-content']//div[contains(@class, 'panel-footer')]/button[@type='submit']
    Wait until page contains  Role updated
    Click button  Close
    Page Should Contain Element  xpath=//input[@value='allan_neece']/../a[text()='Admin']

I can remove the Producer role from Allan
    I can open the workspace member settings tab
    Click element  xpath=//input[@value='allan_neece']/../a[text()='Produce']
    Wait until page contains  Remove special role
    Click Link  Remove special role
    Wait until element is visible  xpath=//div[@class='panel-content']//button[@value='role']
    Click Button  I am sure, remove role now
    Wait until page contains  Role updated
    Click button  Close
    Page Should Not Contain Element  xpath=//input[@value='allan_neece']/../a[text()='Produce']

I can change Allan's role to Moderator
    I can open the workspace member settings tab
    Wait until page contains element  xpath=//input[@value='allan_neece']/../a[text()='Produce']
    Click element  xpath=//input[@value='allan_neece']/../a[text()='Produce']
    Wait until page contains element  xpath=//*[contains(@class, 'tooltip-container')]//a[text()='Change role']
    Click Link  xpath=//*[contains(@class, 'tooltip-container')]//a[text()='Change role']
    Select From List  css=select[name=role]  Moderators
    Click Button  xpath=//div[@id='document-content']//div[contains(@class, 'panel-footer')]/button[@type='submit']
    Wait until page contains element  xpath=//input[@value='allan_neece']/../a[text()='Moderate']

I can remove Allan from the workspace members
    I can open the workspace member settings tab
    Click link  xpath=//div[@id='member-list-functions']//a[text()='Select']
    Wait until element is visible    css=button[value='remove']
    Click Element  xpath=//input[@value='allan_neece']/..
    Click Button  Remove
    Wait until element is visible  xpath=//div[@id='document-content']//div[contains(@class, 'panel-footer')]/button[@type='submit']
    Click Button  Ok
    Wait until element is visible   css=div.pat-notification-panel.success
    Page Should Not Contain Element  xpath=//input[@value='allan_neece']/..

The breadcrumbs show the name of the workspace
    Page Should Contain Element  xpath=//a[@id='breadcrumbs-1' and text()='Open Market Committee']

I can enter the Manage Information Folder
    Click Link  link=Documents
    Page Should Contain  Manage Information
    Click Element  xpath=//form[@id='items']/fieldset/label/a[contains(@href, 'open-market-committee/manage-information')]
    Wait Until Page Contains  Preparation of Records
    Wait Until Page Contains  How to prepare records

I can enter the Projection Materials Folder
    Click Link  link=Documents
    Page Should Contain  Projection Materials
    Click Element  xpath=//form[@id='items']/fieldset/label/a[contains(@href, 'open-market-committee/projection-materials')]
    Wait Until Page Contains  Projection Material
    Wait Until Page Contains  Projection Materials
    Wait Until Page Contains  Open Market Committee

Go back to the workspace by clicking the parent button
    Page Should Contain Element  xpath=//div[@id='selector-contextual-functions']/a[text()='Open Market Committee']
    Click Element  xpath=//div[@id='selector-contextual-functions']/a[text()='Open Market Committee']
    Wait Until Page Contains  Projection Materials

I can search for items
    Page Should Not Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Public bodies reform']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Manage Information']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Projection Materials']
    Input Text  xpath=//input[@name='sidebar-search']  Info
    Wait Until Page Contains Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Public bodies reform']
    Page Should Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Manage Information']
    Page Should Not Contain Element  xpath=//form[@id='items']/fieldset/label/a/strong[text()='Projection Materials']

I can see that the workspace is archived
    [arguments]  ${title}
    Wait until page contains element  xpath=//a/strong[text()='Archived']

I see the option to create a document
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content input[name=title]

I can create a new document
    [arguments]  ${title}
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content input[name=title]
    Input Text  css=.panel-content input[name=title]  text=${title}
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  xpath=//*[@id="meta"]/div[1]/span/textarea[text()='${title}']

I cannot create a new document
    Click link  Documents
    Wait until page contains  Expand sidebar
    Page Should Not Contain   Create document
    Page Should Not Contain Link  Functions

I can create a new folder
    Click link  Documents
    Click link  Functions
    Click link  Create folder
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=My Humble Folder
    Input Text  css=.panel-content textarea[name=description]  text=The description of my humble folder
    Click Button  css=#form-buttons-create
    # We cannot jet test the folders existence without reloading
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    # On reload the navbar is closed by default - open it
    Click link  Documents
    Page Should Contain Element  css=a.pat-inject[href$='/open-market-committee/my-humble-folder']

I can edit the new folder
    Click Element  jquery=.item .title:contains(My Humble Folder)
    Wait until element is visible  jquery=.folder-title:contains(My Humble Folder) .icon-pencil
    Click element  jquery=.folder-title:contains(My Humble Folder) .icon-pencil
    Wait until element is visible  jquery=.panel-body [name=title]
    Input Text  jquery=.panel-body [name=title]  My Superpowered Folder
    Input Text  jquery=.panel-body [name=description]  The description of my superpowered folder
    Click Element  jquery=.panel-footer #form-buttons-edit
    Wait until element is visible  jquery=.folder-title:contains(My Superpowered Folder)

I can create a new image
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=My Image
    Input Text  css=.panel-content textarea[name=description]  text=The description of my humble image
    Click Element  css=label.icon-file-image
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  xpath=//*[@id="meta"]/div/span/textarea[text()='My Image']

I can create a structure
    Click link  Documents
    Click link  Create folder
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=Another Folder
    Click Button  css=#form-buttons-create
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click link  Documents
    Click Element  css=a.pat-inject[href$='/open-market-committee/another-folder']
    Wait Until Page Contains Element  css=a.pat-inject[href$='/open-market-committee']
    Click link  Documents
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=Document in subfolder
    Click Button  css=#form-buttons-create
    Wait until page does not contain element   xpath=//div[@id='document-body']/div[contains(@class, 'injecting')]
    # This must actually test for the document content of the rendered view
    Wait Until Page Contains Element  xpath=//*[@id="meta"]/div[1]/span/textarea[text()='Document in subfolder']
    Wait until page does not contain element   xpath=//div[@id='application-body']/div[contains(@class, 'injecting')]
    Click Button  Save
    Wait until page does not contain element   xpath=//div[@id='application-body']/div[contains(@class, 'injecting')]
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click link  Documents
    Click element  xpath=//a/strong[contains(text(), 'Another Folder')]
    Wait Until Page Contains Element  xpath=//a[@class='pat-inject follow pat-switch'][contains(@href, '/document-in-subfolder')]

I can create a new event
    [arguments]  ${title}  ${start}  ${end}  ${organizer}=Allan Neece  ${invitees}=Dollie Nocera
    Click link  Events
    Click Link  Create event
    Wait Until Page Contains Element  css=.panel-content form .panel-body
    Input Text  css=.panel-content input[name=title]  text=${title}
    Input Text  css=.panel-content input[name=end]  text=${end}
    Input Text  css=.panel-content input[name=start]  text=${start}
    Input text  xpath=//input[@placeholder='Name of organiser']/../div//input  ${organizer}
    Wait Until Element Is Visible  xpath=//span[@class='select2-match'][text()='${organizer}']
    Click Element  xpath=//span[@class='select2-match'][text()='${organizer}']
    Input text  xpath=//input[@placeholder='Invitees']/../div//input  ${invitees}
    Wait Until Element Is Visible  xpath=//span[@class='select2-match'][text()='${invitees}']
    Click Element  xpath=//span[@class='select2-match'][text()='${invitees}']
    Click Button  css=#form-buttons-create
    Wait Until Page Contains  Item created
    Click Button  Close


I cannot create a new event
    [arguments]  ${title}  ${start}  ${end}  ${organizer}=Allan Neece  ${invitees}=Dollie Nocera
    Click link  Events
    Click Link  Create event
    Wait Until Page Contains Element  css=.panel-content form .panel-body
    Input Text  css=.panel-content input[name=title]  text=${title}
    Input Text  css=.panel-content input[name=end]  text=${end}
    Input Text  css=.panel-content input[name=start]  text=${start}
    Input text  xpath=//input[@placeholder='Name of organiser']/../div//input  ${organizer}
    Wait Until Element Is Visible  xpath=//span[@class='select2-match'][text()='${organizer}']
    Click Element  xpath=//span[@class='select2-match'][text()='${organizer}']
    Input text  xpath=//input[@placeholder='Invitees']/../div//input  ${invitees}
    Wait Until Element Is Visible  xpath=//span[@class='select2-match'][text()='${invitees}']
    Click Element  xpath=//span[@class='select2-match'][text()='${invitees}']
    Element Should Be Visible  jquery=#form-buttons-create:disabled

I can edit an event
    [arguments]  ${title}  ${start}  ${end}  ${timezone}
    Wait Until Page Contains Element  xpath=//h3[text()='Older events']
    Click Element  xpath=//h3[text()='Older events']
    Wait until element is visible  jquery=.event-list a:contains("${title}")
    Click Element  jquery=.event-list a:contains("${title}")
    Wait Until Page Contains Element  css=div.event-details
    Input Text  css=.meta-bar textarea[name=title]  text=${title} (updated)
    Input Text  css=div.event-details input[name=start]  text=${start}
    Input Text  css=div.event-details input[name=end]  text=${end}
    Click Element   css=input[name='location']
    Select From List  timezone  ${timezone}
    Click Button  Save
    Wait Until Element Is Visible  css=div.pat-notification-panel.success
    Wait Until Page Contains  Your changes have been saved.
    Click Button  Close
    Wait Until Page Contains Element  jquery=#workspace-events a:contains(updated)
    Textfield Value Should Be  start  ${start}
    List selection should be  timezone  ${timezone}
    Element should contain  css=#workspace-events [href$="open-market-committee/christmas#document-body"]  ${title} (updated)

I cannot edit an event because of validation
    [arguments]  ${title}  ${start}  ${end}  ${timezone}
    Reload Page
    Click link  Events
    Click Element  xpath=//h3[text()='Older events']
    Wait until element is visible  jquery=.event-list a:contains("${title}")
    Click link  jquery=a:contains("${title}")
    Wait Until Page Contains Element  css=div.event-details
    Input Text  css=.meta-bar textarea[name=title]  text=${title} (updated)
    Input Text  css=div.event-details input[name=start]  text=${start}
    Input Text  css=div.event-details input[name=end]  text=${end}
    Select From List  timezone  ${timezone}
    Element Should Be Visible  jquery=#save-event:disabled

Then I can delete an event
    [arguments]  ${title}
    Click link  jquery=a:contains("${title}")
    Wait Until Page Contains Element  css=div.event-details
    ### The following sleep statement addresses the StaleElementReferenceException that sometimes occurs
    ### Solutions proposed on the web address this programmatically with a combination of looping
    ### and exception handling. I wouldn't know of an equivalent solution in robot.
    sleep  2
    Wait until element is visible  css=.meta-bar .icon-trash
    Click Element  css=.meta-bar .icon-trash
    Wait until page contains element    xpath=//div[@class='panel-content']//button[@name='form.buttons.Delete']
    Click Button  I am sure, delete now
    Wait Until Page Contains  has been deleted
    Element should not be visible  css=#workspace-documents
    Element should be visible  css=#workspace-events
    Element should not be visible  jquery=a:contains("${title}")

The file appears in the sidebar
    Wait until Page contains Element  xpath=//fieldset/label/a/strong[text()='bärtige_flößer.odt']

The upload appears in the stream
    Wait until Page contains Element  xpath=//a[@href='activity-stream']//section[contains(@class, 'preview')]//img[contains(@src, 'bärtige_flößer.odt')]

# The self-healing Close messages below are a source of Heisenbugs in the test

I submit the content item
    Wait until element is visible  xpath=//fieldset[@id='workflow-menu']
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Pending')]
    Wait until page contains  The workflow state has been changed
    Wait until page contains  Close
    Click button  Close
    Wait until page does not contain  The workflow state has been changed

I retract the content item
    Wait until element is visible  xpath=//fieldset[@id='workflow-menu']
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Draft')]
    Wait until page contains  The workflow state has been changed
    Wait until page contains  Close
    Click button  Close
    Wait until page does not contain  The workflow state has been changed

I can publish the content item
    Wait until element is visible  xpath=//fieldset[@id='workflow-menu']
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Published')]
    Wait Until Element Is Visible   xpath=//fieldset[@id='workflow-menu']//select/option[@selected='selected' and contains(text(), 'Published')]
    Click button  Close
    Wait until page does not contain  The workflow state has been changed

I cannot publish the content item
    Click element    xpath=//fieldset[@id='workflow-menu']
    Element should be visible   xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Draft')]
    Element should not be visible   xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Published')]

I can edit the document
    Element should be visible  xpath=//div[@id='document-body']//div[@id='editor-toolbar']
    Element should be visible  xpath=//div[@id='document-body']//div[@class='meta-bar']//button[@type='submit']

I cannot edit the document
    Element should not be visible  xpath=//div[@id='document-body']//div[@id='editor-toolbar']
    Element should not be visible  xpath=//div[@id='document-body']//div[@class='meta-bar']//button[@type='submit']

I can see the document
    [arguments]  ${title}
    Click link  Documents
    Page should contain  ${title}

I cannot see the document
    [arguments]  ${title}
    Click link  Documents
    Page should not contain  ${title}

Allan has the option to create a document
    I am logged in as the user allan_neece
    I go to the Shareholder Information Workspace
    I see the option to create a document

# *** workspace and case content related keywords ***

I browse to a workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Documents
    Click Link  link=Manage Information

I browse to a Consumer workspace
    Go To  ${PLONE_URL}/workspaces/service-announcements
    Click Link  link=Documents

I browse to a document
    I browse to a workspace
    Wait Until Page Contains Element  xpath=//a[contains(@href, 'repurchase-agreements')]
    Click Link  xpath=//a[contains(@href, 'repurchase-agreements')]

I view the document
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/repurchase-agreements

I browse to an image
    I browse to a workspace
    Wait Until Page Contains Element  xpath=//a[contains(@href, 'budget-proposal')]
    Click Link  xpath=//a[contains(@href, 'budget-proposal')]

I view the image
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/budget-proposal/view

I upload a new image
    Wait Until Page Contains Element  link=Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Choose File  css=input[name=image]  ${UPLOADS}/vision-to-product.png
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved.
    Click Button  Close

I browse to a file
    I browse to a workspace
    Wait Until Page Contains Element  xpath=//a[contains(@href, 'minutes')]
    Click Link  xpath=//a[contains(@href, 'minutes/view')]

I view the file
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/minutes/view

I upload a new file
    Wait Until Page Contains Element  link=Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Choose File  css=input[name=file]  ${UPLOADS}/bärtige_flößer.odt
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved.
    Click Button  Close

I view the folder
    Go To  ${PLONE_URL}/workspaces/open-market-committee/manage-information/projection-materials/view

I view the task
    Go To  ${PLONE_URL}/workspaces/example-case/populate-metadata

I change the title
    Comment  Toggle the metadata to give the JavaScript time to load
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Input Text  title  New title ♥
    Wait Until Page Contains  New title ♥
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

The document has the new title
    Wait Until Page Contains Element  xpath=//div[@id='document-body']//textarea[@name='title'][text()='New title ♥']

I change the description
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Wait until element is visible  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]
    Input Text  xpath=//textarea[@name='description']  New description ☀
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

The document has the new description
    Page Should Contain  New description ☀

I tag the item
    [arguments]  ${tag}
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Wait until element is visible  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]
    Input Text  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]  ${tag},
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

I tag the item with a suggestion
    [arguments]  ${search_for}  ${selection}
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Wait until element is visible  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]
    Input text  xpath=//input[@placeholder='Tags']/../div//input  ${search_for}
    Wait until element is visible  xpath=//div[@class='select2-result-label'][contains(text(), '${selection}')]
    Click Element  xpath=//div[@class='select2-result-label'][contains(text(), '${selection}')]
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

I clear the tag for an item
    Wait Until Page Contains  Toggle extra metadata
    Click Link  link=Toggle extra metadata
    Wait until element is visible  xpath=//fieldset[@id='meta-extra']//input[contains(@class, 'select2-input')]
    Click Link  css=.select2-search-choice-close
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Click Button  Close
    Wait Until Page Does Not Contain  Your changes have been saved

The metadata has the new tag
    Click Link  link=Toggle extra metadata
    Page Should Contain  NewTag☃

# *** case related keywords ***

I am in a case workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Example Case

I am in a case workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Example Case

I move the example workspace to state prepare
      I can go to the Example Case
      I can go to the sidebar tasks tile of my case
      I can open a milestone task panel  prepare
      I select the task check box  Draft proposal
      I select the task check box  Budget
      I select the task check box  Stakeholder feedback

I move the example workspace to state complete
      I move the example workspace to state prepare
      I can close a milestone  prepare
      I can open a milestone task panel  complete
      I select the task check box  Quality check

Admin moves the example workspace to state complete
      I am in a case workspace as a workspace admin
      I move the example workspace to state complete

I can create a new case
    [arguments]  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal
    Input Text  name=title  text=${title}
    Input Text  name=description  text=Let's get organized
    Select From List  workspace-type  case-template
    Wait Until Page Contains  Case Template
    Click Button  Create workspace
    Wait Until Page Contains  Populate Metadata

I can create a new template case
    [arguments]  ${title}
    Go To  ${PLONE_URL}/templates/++add++ploneintranet.workspace.case
    Input Text  form.widgets.IBasic.title  New template
    Click Button  Save
    Go To  ${PLONE_URL}/workspaces

I can create a new case from a template
    [arguments]  ${template}  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal
    Input Text  name=title  text=${title}
    Input Text  name=description  text=Something completely different
    Select From List  workspace-type  case-template
    Wait Until Page Contains  Case Template
    Click Button  Create workspace
    Wait Until Page Contains  Item created

I can delete a case
    [arguments]  ${case_id}
    Go To  ${PLONE_URL}/workspaces/${case_id}/delete_confirmation
    Wait until page contains element    xpath=//div[@class='buttons panel-footer']//button[@name='form.buttons.Delete']
    Click Button    I am sure, delete now
    Wait Until Page Contains    has been deleted

I can delete a template case
    [arguments]  ${case_id}
    Go To  ${PLONE_URL}/templates/${case_id}/delete_confirmation
    Wait until page contains element    xpath=//div[@class='buttons panel-footer']//button[@name='form.buttons.Delete']
    Click Button    I am sure, delete now
    Wait Until Page Contains    has been deleted

I go to the dashboard
    Go To  ${PLONE_URL}

I select the task centric view
    Select From List  dashboard  Task centric view
    Wait Until Page Contains  Tasks

I mark a new task complete
    Wait until element is visible  xpath=(//a[@title='Todo soon'])
    Select Checkbox  xpath=(//a[@title='Todo soon'])[1]/preceding-sibling::input[@name="active-tasks:list"]
    Wait until Page Contains  Task state changed

I select the task check box
    [arguments]  ${title}
    Wait until Page Contains Element  xpath=(//label[@class='unchecked']//a[@title='${title}'])
    Select Checkbox  xpath=(//a[@title='${title}'])/preceding-sibling::input[@name="active-tasks:list"]
    ### Without the following sleep statement the 'Wait until' statement that follows it
    ### is executed quickly and selenium sometimes leaves the page before autosave can happen.
    ### This leads to errors later on when the box is assumed to be checked.
    sleep  4
    Wait until Page Contains Element  xpath=(//label[@class='checked']//a[@title='${title}'])

I unselect the task check box
    [arguments]  ${title}
    Wait until Page Contains Element  xpath=(//label[@class='checked']//a[@title='${title}'])
    Unselect Checkbox  xpath=(//a[@title='${title}'])/preceding-sibling::input[@name="active-tasks:list"]
    ### Without the following sleep statement the 'Wait until' statement that follows it
    ### is executed quickly and selenium sometimes leaves the page before autosave can happen.
    ### This leads to errors later on when the box is assumed to be checked.
    sleep  4
    Wait until Page Contains Element  xpath=(//label[@class='unchecked']//a[@title='${title}'])

I see a task is complete
    [arguments]  ${title}
    Wait until Page Contains Element  xpath=(//label[@class='checked']//a[@title='${title}'])

I see a task is open
    [arguments]  ${title}
    Wait until Page Contains Element  xpath=(//label[@class='unchecked']//a[@title='${title}'])

I see the task quality check has state
    [arguments]  ${state}
    Go To  ${PLONE_URL}/workspaces/example-case/quality-check
    Element should be visible  xpath=//fieldset[@id='workflow-menu']/label[@data-option='${state}']

I do not see the completed task is not listed
    Page Should Not Contain  Todo soon

I can go to the sidebar tasks tile of my case
    Click Link  link=Tasks
    Wait Until Page Contains  General tasks

I can add a new task
    [arguments]  ${title}  ${username}  ${milestone}=
    Click Link  Create task
    Wait Until Page Contains Element  css=.panel-body
    Input Text  xpath=//div[@class='panel-body']//input[@name='title']  text=${title}
    Input Text  xpath=//div[@class='panel-body']//textarea[@name='description']  text=Plan for success
    Element Should Contain  xpath=//label[@class='initiator']//li[@class='select2-search-choice']/div  Allan Neece
    Input Text  css=label.assignee li.select2-search-field input  ${username}
    Wait Until Element Is visible  xpath=//span[@class='select2-match'][text()='${username}']
    Click Element  xpath=//span[@class='select2-match'][text()='${username}']
    Select From List  milestone  ${milestone}
    Click Button  Create
    Wait Until Page Contains  ${title}

I can close a milestone
    [arguments]  ${milestone}
    I can open a milestone task panel  ${milestone}
    Wait Until Page Contains Element  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Close milestone']
    Click Link  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Close milestone']
    [Documentation]  Wait until the temporary class 'injecting' has been removed, to be sure injection has completed
    Wait until page does not contain element   xpath=//div[@id='workspace-tickets']/div[contains(@class, 'injecting')]
    # auto-closes current, reopen
    I can open a milestone task panel  ${milestone}
    Wait until element is visible  xpath=//fieldset[@id='milestone-${milestone}']//h4[contains(@class, 'state-finished')]

I cannot close a milestone
    [arguments]  ${milestone}
    I can open a milestone task panel  ${milestone}
    Element should not be visible  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Close milestone']

I can reopen a milestone
    [arguments]  ${milestone}
    I can open a milestone task panel  ${milestone}
    Wait until element is visible  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Reopen milestone']
    Click Link  xpath=//fieldset[@id='milestone-${milestone}']//a[text()='Reopen milestone']
    [Documentation]  Wait until the temporary class 'injecting' has been removed, to be sure injection has completed
    Wait until page does not contain element   xpath=//div[@id='workspace-tickets']/div[contains(@class, 'injecting')]
    # auto-closes current, reopen
    I can open a milestone task panel  ${milestone}
    Wait until element is visible  xpath=//fieldset[@id='milestone-${milestone}']//h4[contains(@class, 'state-finished')]

I can open a milestone task panel
    [arguments]  ${milestone}
    # panel 'open' state is session dependent, force open
    Run Keyword And Ignore Error  Click Element  css=#milestone-${milestone}.closed h4

I can see the user is a guest
    [arguments]  ${username}
    Wait until page contains element  xpath=//form[@id='member-list-items']/fieldset[@id='existing_guests']//strong[@class='title' and contains(text(), '${username}')]
    Page should not contain element  xpath=//form[@id='member-list-items']/fieldset[@id='existing_users']//strong[@class='title' and contains(text(), '${username}')]

I write a status update
    [arguments]  ${message}
    Wait Until Element Is visible  css=textarea.pat-content-mirror
    Element should not be visible  css=button[name='form.buttons.statusupdate']
    Click element  css=textarea.pat-content-mirror
    Wait Until Element Is visible  css=button[name='form.buttons.statusupdate']
    Input Text  css=textarea.pat-content-mirror  ${message}

I post a status update
    [arguments]  ${message}
    I write a status update    ${message}
    I submit the status update

I submit the status update
    Click button  css=button[name='form.buttons.statusupdate']

I open the post action menu
    [arguments]  ${message}
    Click Link  xpath=//section[@class='post-content']//p[contains(text(), '${message}')]/../..//a[contains(@class, 'icon-cog')]

I cannot open the post action menu
    [arguments]  ${message}
    Page should not contain link  xpath=//section[@class='post-content']//p[contains(text(), '${message}')]/../..//a[contains(@class, 'icon-cog')]

I open the comment action menu
    [arguments]  ${message}
    Click Link  xpath=//section[@class='comment-content']//p[contains(text(), '${message}')]/../..//a[contains(@class, 'icon-cog')]

I cannot open the comment action menu
    [arguments]  ${message}
    Page should not contain link  xpath=//section[@class='comment-content']//p[contains(text(), '${message}')]/../..//a[contains(@class, 'icon-cog')]

I delete the status update
    [arguments]  ${message}
    I open the post action menu  ${message}
    Click Link  Delete post
    Click Button  I am sure, delete now

I can see the status delete confirmation
    Wait Until Page Contains    This post has been succesfully deleted.

I delete the status reply
    [arguments]  ${message}
    I open the comment action menu  ${message}
    Click Link  Delete comment
    Click Button  I am sure, delete now

I can see the status reply delete confirmation
    Wait Until Page Contains    This comment has been succesfully deleted.

I can edit the status update
    [arguments]  ${message1}  ${message2}
    I open the post action menu  ${message1}
    Click Link  Edit post
    Input Text  xpath=//textarea[contains(text(), '${message1}')]  ${message2}
    Click Button  Save
    Wait Until Page Contains  Edited

I can edit the status reply
    [arguments]  ${message1}  ${message2}
    I open the comment action menu  ${message1}
    Click Link  Edit comment
    Input Text  xpath=//textarea[contains(text(), '${message1}')]  ${message2}
    Click Button  Save
    Wait Until Page Contains  Edited

I can access the original text
    [arguments]  ${message1}  ${message2}
    Click Link  xpath=//div[@id='activity-stream']//div[@class='post item']//section[@class='post-content']//p[contains(text(), '${message2}')]/a[contains(@class, 'edited-toggle')]
    Comment  Working around some Selenium limitations here
    Wait Until Element Is Visible  //section[contains(@class, 'original-text')]//p/strong
    Page Should Contain  ${message1}

I can access the original reply text
    [arguments]  ${message1}  ${message2}
    Click Link  xpath=//div[@id='activity-stream']//div[@class='comment']//section[@class='comment-content']//p[contains(text(), '${message2}')]/a[contains(@class, 'edited-toggle')]
    Comment  Working around some Selenium limitations here
    Wait Until Element Is Visible  //section[contains(@class, 'original-text')]//p/strong
    Page Should Contain  ${message1}

I can mention the user
    [arguments]  ${username}
    Click link    link=Mention people
    Wait Until Element Is visible  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username}')]/../..
    Click element  xpath=//form[@id='postbox-users']//label/a/strong[contains(text(), '${username}')]/../..
    Wait Until Element Is visible  xpath=//p[@class='content-mirror']//a[contains(text(), '@${username}')][1]
    Click element    css=textarea.pat-content-mirror

I freeze the case
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click link  Freeze case

I unfreeze the case
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click link  Unfreeze case

I unfreeze the case via the metromap
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click link  Unfreeze
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click Button  I am sure, unfreeze now

I see that the workspace is frozen
    Wait Until Page Contains  Frozen

I see that the workspace is not frozen
    Page Should Not Contain  Frozen

# *** search related keywords ***

I can see the site search button
    Page Should Contain Element  css=#global-header input.search

I can search in the site header for ${SEARCH_STRING}
    Input text  css=#global-header input.search  ${SEARCH_STRING}
    Submit Form  css=#global-header form#global-nav-search

I can see the search result ${SEARCH_RESULT_TITLE}
    Element should be visible  jquery=.results a:contains("${SEARCH_RESULT_TITLE}")

I cannot see the search result ${SEARCH_RESULT_TITLE}
    Element should not be visible  link=${SEARCH_RESULT_TITLE}

I can follow the search result ${SEARCH_RESULT_TITLE}
    Click Link  jquery=.results a:contains("${SEARCH_RESULT_TITLE}")
    Page should contain  ${SEARCH_RESULT_TITLE}

I can filter content of type ${CONTENT_TYPE}
    [Documentation]  We remove the classes we will look at to see if the injection is completed
    Execute Javascript  jQuery('.previews-on,.previews-off').removeClass('previews-on').removeClass('previews-off')
    Select Checkbox  css=input[type="checkbox"][value="${CONTENT_TYPE}"]
    Wait Until Element is Visible  css=.previews-on,.previews-off

I can unfilter content of type ${CONTENT_TYPE}
    [Documentation]  We remove the classes we will look at to see if the injection is completed
    Execute Javascript  jQuery('.previews-on,.previews-off').removeClass('previews-on').removeClass('previews-off')
    Unselect Checkbox  css=input[type="checkbox"][value="${CONTENT_TYPE}"]
    Wait Until Element is Visible  css=.previews-on,.previews-off

The search results do not contain ${STRING_IN_SEARCH_RESULTS}
    Wait Until Keyword Succeeds  1  3  Page should not contain  ${STRING_IN_SEARCH_RESULTS}

I can set the date range to ${START_DATE} ${END_DATE}
    Input Text  start_date  \
    Focus  jquery=[name=start_date]
    Press Key  jquery=[name=start_date]  ${START_DATE}
    Input Text  end_date  \
    Focus  jquery=[name=end_date]
    Press Key  jquery=[name=end_date]  ${END_DATE}
    Press Key  jquery=[name=end_date]  \n
    Wait Until Element is Visible  css=dl.search-results[data-search-string*="start_date=${START_DATE}"]
    Wait Until Element is Visible  css=dl.search-results[data-search-string*="end_date=${END_DATE}"]

I toggle the search previews
    Click Element  css=[href="#view-options"]
    Wait Until Element is Visible  jquery=.tooltip-container label:contains("Display previews")
    [Documentation]  We remove the classes we will look at to see if the injection is completed
    Execute Javascript  jQuery('.previews-on,.previews-off').removeClass('previews-on').removeClass('previews-off')
    Click Element  jquery=.tooltip-container label:contains("Display previews")
    Wait Until Element is Visible  css=.previews-on,.previews-off

I can see the search result previews
    Wait Until Element is Visible  css=.previews-on .preview

I cannot see the search result previews
    Wait Until Element is Visible  css=.previews-off

I can see that the first search result is ${RESULT_TITLE}
    Wait Until Element is Visible  jquery=.search-results > :first-child > a:contains(${RESULT_TITLE})

I can sort search results by ${FIELD}
    Click Element  css=[href="#view-options"]
    Wait Until Element is Visible  jquery=.tooltip-container label:contains("Sort by ${FIELD}")
    [Documentation]  We remove the classes we will look at to see if the injection is completed
    Execute Javascript  jQuery('.previews-on,.previews-off').removeClass('previews-on').removeClass('previews-off')
    Click Element  jquery=.tooltip-container label:contains("Sort by ${FIELD}")
    Wait Until Element is Visible  css=.previews-on,.previews-off

I can click the ${TAB_NAME} tab
    Click Link  link=${TAB_NAME}
    Wait Until Page Does Not Contain Element  css=.injecting-content

# *** END search related keywords ***

# *** bookmark related keywords ***

I can bookmark the application
    [arguments]  ${application}
    I can click the Apps tab
    Click element  xpath=//h3[contains(text(),'${application}')]/../../a[contains(text(), 'Bookmark')]
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click button  Close
    I can click the Apps tab
    Page should contain element  xpath=//h3[contains(text(), '${application}')]/../../a[contains(text(), 'Remove bookmark')]

I can unbookmark the application
    [arguments]  ${application}
    I can click the Apps tab
    Click element  xpath=//h3[contains(text(),'${application}')]/../../a[contains(text(), 'Remove bookmark')]
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click button  Close
    I can click the Apps tab
    Page should contain element  xpath=//h3[contains(text(), '${application}')]/../../a[contains(text(), 'Bookmark')]

I can bookmark the workspace
    [arguments]  ${workspace}
    I can click the Workspaces tab
    Click element  xpath=//h3[contains(text(),'${workspace}')]/../../a[contains(text(), 'Bookmark')]
    Wait Until Page Does Not Contain Element  css=.injecting-content
    I can click the Workspaces tab
    Page should contain element  xpath=//h3[contains(text(), '${workspace}')]/../../a[contains(text(), 'Remove bookmark')]

I can unbookmark the workspace
    [arguments]  ${workspace}
    I can click the Workspaces tab
    Click element  xpath=//h3[contains(text(),'${workspace}')]/../../a[contains(text(), 'Remove bookmark')]
    Wait Until Page Does Not Contain Element  css=.injecting-content
    I can click the Workspaces tab
    Page should contain element  xpath=//h3[contains(text(), '${workspace}')]/../../a[contains(text(), 'Bookmark')]

Bookmark the current context
    Click Element  jquery=.quick-functions :contains('Bookmark')
    Wait Until Page Contains Element  jquery=.pat-notification-panel :contains('Close')
    Click Element  jquery=.pat-notification-panel :contains('Close')
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Page should contain element  jquery=.quick-functions :contains('Remove bookmark')

Unbookmark the current context
    Click Element  jquery=.quick-functions :contains('Remove bookmark')
    Wait Until Page Contains Element  jquery=.pat-notification-panel :contains('Close')
    Click Element  jquery=.pat-notification-panel :contains('Close')
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Page should contain element  jquery=.quick-functions :contains('Bookmark')

I can bookmark the workspace document
    [arguments]  ${document}
    I open the sidebar documents tile
    Click Element  xpath=//strong[contains(text(), 'Manage Information')]/..
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click Element  xpath=//strong[contains(text(), '${document}')]/..
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Bookmark the current context

I can unbookmark the workspace document
    [arguments]  ${document}
    I open the sidebar documents tile
    Click Element  xpath=//strong[contains(text(), 'Manage Information')]/..
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click Element  xpath=//strong[contains(text(), '${document}')]/..
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Unbookmark the current context

I can bookmark the task
    [arguments]  ${task}
    I can go to the Example Case
    I can go to the sidebar tasks tile of my case
    Click link  ${task}
    Bookmark the current context

I can unbookmark the task
    [arguments]  ${task}
    I can go to the Example Case
    I can go to the sidebar tasks tile of my case
    Click link  ${task}
    Unbookmark the current context

I can go to the bookmark application
    I can Click the Apps tab
    Click Element  jquery=h3:contains(Bookmarks)
    Wait until element is visible  jquery=.bookmark :contains(Example Case)

I can filter bookmarked application
    Input text  jquery=.application-bookmarks [name=SearchableText]  bookmark
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Page should contain element  jquery=.bookmark :contains(Bookmark)
    Page should not contain element  jquery=.bookmark :contains(Example Case)

I can filter bookmarked content
    Input text  jquery=.application-bookmarks [name=SearchableText]  example
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Page should contain element  jquery=.bookmark :contains(Example Case)
    Page should not contain element  jquery=.bookmark :contains(Bookmark)

I can see the bookmarked applications
    Click Element  jquery=[href=#directory-apps]
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Page should contain element  css=.tile.app-bookmarks

I can see the bookmarked workspaces
    Click Element  jquery=[href=#directory-workspaces]
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Page should contain element  css=.tile.workspace-example-case

I can see the bookmarked documents
    Click Element  jquery=[href=#directory-documents]
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Page should contain element  jquery=figcaption:contains('Budget Proposal')

I can see bookmark grouped by workspace
    Select From List  group_by  workspace
    Wait Until Page Does Not Contain Element  css=.injecting-content
    # I can see a ws
    Page should contain element  xpath=//h3[contains(text(), 'Example Case')]/../ul/li/a[contains(text(), 'Example Case')]
    # a document inside it
    Page should contain element  xpath=//h3[contains(text(), 'Example Case')]/../ul/li/a[contains(text(), 'Draft proposal')]
    # and somethign unrelated
    Page should contain element  xpath=//h3[contains(text(), 'Not in a workspace')]/../ul/li/a[contains(text(), 'Bookmark')]

I can see bookmark grouped by creation date
    Select From List  group_by  created
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Page should contain element  xpath=//h3[contains(text(), 'All time')]/../ul/li/a[contains(text(), 'Bookmarks')]

I can see the bookmarks tile in the dashboard
    I open the Dashboard
    I can see in the bookmark tile that the last bookmark is  Shareholder information

I can query the bookmarks tile for
    [arguments]  ${query}
    Input Text  jquery=#portlet-bookmarks-dashboard [name=SearchableText]  ${query}
    Wait Until Page Does Not Contain Element  css=.injecting-content

I can see in the bookmark tile that the last bookmark is
    [arguments]  ${text}
    Element should contain  jquery=#bookmarks-search-items-dashboard li:last a  ${text}

I can see in the bookmark tile that we have no bookmarks matching
    [arguments]  ${text}
    Element should contain  jquery=#bookmarks-search-items-dashboard .pat-message  No bookmarks were found matching ${text}

# *** END bookmark related keywords ***

# *** mail related keywords ***

I can inspect mail metadata
    Click Link  jquery=a:contains("Files for application 2837")
    Wait Until Page Does Not Contain Element  css=.injecting-content
    Click Link  jquery=.meta-data-toggle
    Element should be visible  jquery=a:contains('pilz@pilzen.de')

# *** END mail related keywords ***
