*** Keywords ***

Prepare test browser
    Open test browser
    Set window size  1024  900

I'm logged in as a '${ROLE}'
    Enable autologin as  ${ROLE}

I am logged in as site administrator
    Element should be visible  css=body.userrole-site-administrator

I am logged in as the user ${userid}
    Go To  ${PLONE_URL}/login
    Input text  name=__ac_name  ${userid}
    Input text  name=__ac_password  secret
    Click button  Login

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

I open the Dashboard
    Go to  ${PLONE_URL}/dashboard.html

I am in a workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Open Market Committee Workspace

I am in a case workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Minifest

I am in a Producers workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Open Parliamentary Papers Guidance Workspace

I am in a Consumers workspace as a workspace member
    I am logged in as the user allan_neece
    I go to the Shareholder Information Workspace

I am in a workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Open Market Committee Workspace

I am in a case workspace as a workspace admin
    I am logged in as the user christian_stoney
    I go to the Minifest

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

I go to the Minifest
    Go To  ${PLONE_URL}/workspaces/minifest
    Wait Until Element Is Visible  css=h1#workspace-name
    Wait Until Page Contains  Minifest

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

I can go to the Open Market Committee Workspace
    Go To  ${PLONE_URL}/workspaces/open-market-committee

I can go to the Minifest
    Go To  ${PLONE_URL}/workspaces/minifest

I am redirected to the login page
    Location Should Contain  require_login


# *** Workspace related keywords ***

I can create a new workspace
    [arguments]  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  xpath=//input[@name='title']  text=${title}
    Input Text  xpath=//textarea[@name='description']  text=Random description
    Click Button  Create workspace
    Wait Until Element Is visible  css=div#activity-stream  timeout=10

I select a file to upload
    [Documentation]  We can't drag and drop from outside the browser so it gets a little hacky here
    Execute JavaScript  jQuery('.pat-upload.upload .accessibility-options').show()
    Execute JavaScript  jQuery('.pat-upload.upload').siblings('button').show()
    Choose File  css=input[name=file]  ${UPLOADS}/bärtige_flößer.odt
    Click Element  xpath=//button[text()='Upload']

I can go to the sidebar info tile
    Click Link  link=Workspace settings and about
    Wait Until Page Contains  General
    Wait Until Page Contains  Workspace title
    Wait Until Page Contains  Workspace brief description

I can go to the sidebar events tile
    Click Link  link=Events
    Wait Until Element Is visible  xpath=//h3[.='Upcoming events']


I can open the workspace security settings tab
    Click Link  link=Workspace settings and about
    Wait until page contains  Security
    Click link  link=Security
    Wait until page contains  Workspace policy

I can open the workspace member settings tab
    Click Link  link=Workspace settings and about
    Click link  link=Members
    Wait until page contains  Members

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

I can see upcoming events
    Page Should Contain Element  xpath=//a[.='Plone Conf']

Older events are hidden
    Element should not be visible  jquery=div#older-events a

I can delete an old event
    Click Element  css=div#older-events h3
    Mouse Over  xpath=//div[@id='older-events']//li[@class='cal-event']
    Focus  xpath=//div[@id='older-events']//li[@class='cal-event']
    Click Element  css=div#older-events button[type='submit']
    Wait Until Page Contains  Do you really want to delete this item
    Click Button  css=#form-buttons-Delete

I can go to the sidebar tasks tile
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click Link  link=Tasks
    Wait Until Element Is visible  xpath=//p[.='No tasks created yet']

I can invite Alice to join the workspace
    Wait Until Page Contains Element  css=div.button-bar.create-buttons a.icon-user-add
    Click Link  css=div.button-bar.create-buttons a.icon-user-add
    I can invite Alice to the workspace

I can invite Alice to join the workspace from the menu
    Wait Until Page Contains Element  link=Functions
    Click Link  link=Functions
    Click Link  xpath=//ul[@class='menu']//a[.='Add user']
    I can invite Alice to the workspace

I can invite Alice to the workspace
    Wait until page contains  Add user
    Input Text  css=li.select2-search-field input  alice
    Wait Until Element Is visible  css=span.select2-match
    Click Element  css=span.select2-match
    Click Button  Ok

The breadcrumbs show the name of the workspace
    Page Should Contain Element  xpath=//a[@id='breadcrumbs-2' and text()='Open Market Committee']

I can enter the Manage Information Folder
    Click Link  link=Documents
    Page Should Contain  Manage Information
    Click Element  xpath=//form[@id='items']/fieldset/label[1]/a
    Wait Until Page Contains  Preparation of Records
    Wait Until Page Contains  How to prepare records

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

I can create a new document
    [arguments]  ${title}
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=${title}
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  css=#content input[value="${title}"]

I cannot create a new document
    Click link  Documents
    Wait until page contains  Test Document
    Page Should Not Contain   Create document
    Click link  Functions
    Page Should Not Contain   Create document

I can create a new folder
    Click link  Documents
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

I can create a new image
    Click link  Documents
    Click link  Functions
    Click link  Create document
    Wait Until Page Contains Element  css=.panel-content form
    Input Text  css=.panel-content input[name=title]  text=My Image
    Input Text  css=.panel-content textarea[name=description]  text=The description of my humble image
    Click Element  css=label.icon-file-image
    Click Button  css=#form-buttons-create
    Wait Until Page Contains Element  css=#content input.doc-title[value='My Image']

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
    # This must actually test for the document content of the rendered view
    Wait Until Page Contains Element  css=#content input[value="Document in subfolder"]
    Click Button  Save
    Wait Until Page Contains  Your changes have been saved
    Go To  ${PLONE_URL}/workspaces/open-market-committee
    Click link  Documents
    Click element  xpath=//a/strong[contains(text(), 'Another Folder')]
    Wait Until Page Contains Element  xpath=//a[@class='pat-inject follow'][contains(@href, '/document-in-subfolder')]

I can create a new event
    [arguments]  ${title}  ${start}  ${end}
    Click link  Events
    Click Link  Create event
    Wait Until Page Contains Element  css=.panel-content form .panel-body
    Input Text  css=.panel-content input[name=title]  text=${title}
    Input Text  css=.panel-content input[name=start]  text=${start}
    Input Text  css=.panel-content input[name=end]  text=${end}
    Click Button  css=#form-buttons-create

I can edit an event
    [arguments]  ${title}  ${start}  ${end}
    Reload Page
    Click link  Events
    Click Element  xpath=//h3[text()='Older events']
    Click link  ${title}
    Wait Until Page Contains Element  css=div.event-details
    Input Text  css=div.event-details input[name=start]  text=${start}
    Input Text  css=div.event-details input[name=end]  text=${end}
    Click Button  Save

The file appears in the sidebar
    Wait until Page contains Element  xpath=//fieldset/label/a/strong[text()='bärtige_flößer.odt']  timeout=20

The upload appears in the stream
    Wait until Page contains Element  xpath=//a[@href='activity-stream']//section[contains(@class, 'preview')]//img[contains(@src, 'bärtige_flößer.odt')]  timeout=20

# The self-healing Close messages below are a source of Heisenbugs in the test

I submit the content item
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Pending')]
    Wait until page contains  The workflow state has been changed
    Wait until page contains  Close
    Click button  Close

I retract the content item
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Draft')]
    Wait until page contains  The workflow state has been changed
    Wait until page contains  Close
    Click button  Close

I can publish the content item
    Click element    xpath=//fieldset[@id='workflow-menu']
    Click Element    xpath=//fieldset[@id='workflow-menu']//select/option[contains(text(), 'Published')]
    Wait Until Element Is Visible   xpath=//fieldset[@id='workflow-menu']//select/option[@selected='selected' and contains(text(), 'Published')]
    Click button  Close

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


# *** case related keywords ***


I can create a new case
    [arguments]  ${title}
    Go To  ${PLONE_URL}/workspaces
    Click Link  link=Create workspace
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  css=input.required.parsley-validated  text=${title}
    Input Text  name=description  text=Let's get organized
    Select From List  portal_type  ploneintranet.workspace.case
    Wait Until Page Contains  Case Template
    Click Button  Create workspace
    Wait Until Page Contains  Basisdatenerfassung

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
    Wait Until Element Is visible  css=div#pat-modal  timeout=5
    Input Text  css=input.required.parsley-validated  text=${title}
    Input Text  name=description  text=Something completely different
    Select From List  portal_type  ploneintranet.workspace.case
    Wait Until Page Contains  New template
    Select Radio Button  template_id  new-template
    Click Button  Create workspace
    Wait Until Page Contains  Item created

I can delete a case
    [arguments]  ${case_id}
    Go To  ${PLONE_URL}/workspaces/${case_id}/delete_confirmation
    Click Button  Delete
    Page Should Contain  has been deleted

I can delete a template case
    [arguments]  ${case_id}
    Go To  ${PLONE_URL}/templates/${case_id}/delete_confirmation
    Click Button  Delete
    Page Should Contain  has been deleted

I go to the dashboard
    Go To  ${PLONE_URL}

I mark a new task complete
    Select Checkbox  xpath=(//a[@title='Todo soon'])[1]/preceding-sibling::input[1]
    Wait Until Page Contains  Changes applied

I select the task check box
    [arguments]  ${title}
    Select Checkbox  xpath=(//a[@title='${title}'])/preceding-sibling::input[1]
    Wait Until Page Contains  Changes applied

I unselect the task check box
    [arguments]  ${title}
    Unselect Checkbox  xpath=(//a[@title='${title}'])/preceding-sibling::input[1]
    Wait Until Page Contains  Changes applied

I see a task is complete
    [arguments]  ${title}
    Checkbox Should Be Selected  xpath=(//a[@title='${title}'])/preceding-sibling::input[1]

I see a task is open
    [arguments]  ${title}
    Checkbox Should Not Be Selected  xpath=(//a[@title='${title}'])/preceding-sibling::input[1]

I do not see the completed task is not listed
    Page Should Not Contain  Todo soon

I can go to the sidebar tasks tile of my case
    Click Link  link=Tasks
    Wait Until Page Contains  Unassigned

I can add a new task
    [arguments]  ${title}
    Click Link  Create task
    Wait Until Page Contains Element  css=.panel-body
    Input Text  xpath=//div[@class='panel-body']//input[@name='title']  text=${title}
    Input Text  xpath=//div[@class='panel-body']//textarea[@name='description']  text=Plan for success
    Element Should Contain  xpath=//label[@class='initiator']//li[@class='select2-search-choice']/div  Christian Stoney
    Input Text  css=label.assignee li.select2-search-field input  stoney
    Wait Until Element Is visible  xpath=//span[@class='select2-match'][text()='Stoney']
    Click Element  xpath=//span[@class='select2-match'][text()='Stoney']
    Select From List  milestone  new
    Click Button  Create
    Wait Until Page Contains  ${title}

I can close the first milestone
    Click Element  xpath=//h4[text()='New']
    Click Link  Close milestone
    Page Should Contain  Item state changed

I can toggle a milestone
    [arguments]  ${milestone}
    Click Element  xpath=//h4[text()='${milestone}']
